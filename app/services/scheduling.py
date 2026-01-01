from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from croniter import croniter

from app.core.db import SessionLocal
from app.models.workflow import Workflow

import httpx
from app.core.config import get_settings
from app.services.alert_detection import check_stuck_workflows, check_runtime_anomalies
from app.services.alert_logger import create_alert
from app.models.alert import AlertType, AlertSeverity

settings = get_settings()



# How long after expected time we wait before calling it "missed"
MISSED_RUN_GRACE_MINUTES = 0

scheduler = AsyncIOScheduler(timezone="UTC")


def check_scheduled_workflows():
    """
    Periodic task:
    - For each active workflow with a cron_expression
    - Compute the last expected run time based on cron
    - Compare with last_run_at
    - If it should have run but didn't → log as MISSED (later: send alert)
    """
    now = datetime.now(timezone.utc)
    db = SessionLocal()

    try:
        workflows = (
            db.query(Workflow)
            .filter(Workflow.active.is_(True))
            .filter(Workflow.cron_expression.isnot(None))
            .all()
        )

        for wf in workflows:
            cron_expr = wf.cron_expression
            if not cron_expr:
                continue

            try:
                itr = croniter(cron_expr, now)
                # last expected run time BEFORE "now"
                last_expected = itr.get_prev(datetime)
            except Exception as e:
                print(
                    f"[monitor] Invalid cron for workflow {wf.id} "
                    f"({cron_expr}): {e}"
                )
                continue

            # Add a grace window (GitHub cron is not perfectly precise)
            grace_deadline = last_expected + timedelta(minutes=MISSED_RUN_GRACE_MINUTES)

            # If we are still before grace deadline, don't judge yet
            if now < grace_deadline:
                continue

            # Get organization-specific threshold
            org_threshold = MISSED_RUN_GRACE_MINUTES
            if wf.repository and wf.repository.organization:
                org_threshold = wf.repository.organization.alert_threshold_minutes or MISSED_RUN_GRACE_MINUTES

            # Adjust grace deadline with org threshold
            grace_deadline = last_expected + timedelta(minutes=org_threshold)

            # Make last_run_at timezone-aware for comparison
            last_run_at = wf.last_run_at
            if last_run_at is not None and last_run_at.tzinfo is None:
                last_run_at = last_run_at.replace(tzinfo=timezone.utc)

            # If last_run_at is None or older than last_expected, it's a MISS
            if last_run_at is None or last_run_at < last_expected:
                # Check if we've already alerted for this miss (to avoid spam)
                # For now, we'll alert every time we detect it
                # In production, you'd want to track "last_alert_sent_at" per workflow

                alert_text = (
                    f"⚠️ *Missed Scheduled Run*\n"
                    f"Workflow: `{wf.name}`\n"
                    f"Repository: `{wf.repository.full_name if wf.repository else 'Unknown'}`\n"
                    f"Expected: {last_expected.strftime('%Y-%m-%d %H:%M UTC')}\n"
                    f"Last Run: {wf.last_run_at.strftime('%Y-%m-%d %H:%M UTC') if wf.last_run_at else 'Never'}\n"
                )
                
                # Get org settings
                if wf.repository and wf.repository.organization:
                    org = wf.repository.organization
                    
                    # Log alert to database
                    create_alert(
                        db=db,
                        organization_id=org.id,
                        workflow_id=wf.id,
                        alert_type=AlertType.MISSED,
                        severity=AlertSeverity.ERROR,
                        message=alert_text
                    )
                    
                    # Send to Slack if configured
                    if org.slack_webhook_url:
                        send_slack_alert(org.slack_webhook_url, alert_text)
                    
                    # Send to Teams if configured
                    if org.teams_webhook_url:
                        send_teams_alert(org.teams_webhook_url, alert_text)
                    
                    if not org.slack_webhook_url and not org.teams_webhook_url:
                        print(f"[monitor] No webhooks configured for org {org.name}")
                else:
                     print(f"[monitor] Workflow {wf.id} has no repo/org linked")

            # DELAYED RUN DETECTION
            # Check if workflow started later than expected
            if wf.last_run_at and wf.repository and wf.repository.organization:
                org = wf.repository.organization
                if org.alert_on_delayed:
                    delay_minutes = (wf.last_run_at - last_expected).total_seconds() / 60
                    if delay_minutes > org_threshold:
                        alert_text = (
                            f"⏰ *Delayed Workflow Start*\n"
                            f"Workflow: `{wf.name}`\n"
                            f"Repository: `{wf.repository.full_name}`\n"
                            f"Expected: {last_expected.strftime('%Y-%m-%d %H:%M UTC')}\n"
                            f"Started: {wf.last_run_at.strftime('%Y-%m-%d %H:%M UTC')}\n"
                            f"Delay: {int(delay_minutes)} minutes\n"
                        )
                        
                        # Log to database
                        create_alert(
                            db=db,
                            organization_id=org.id,
                            workflow_id=wf.id,
                            alert_type=AlertType.DELAYED,
                            severity=AlertSeverity.WARNING,
                            message=alert_text
                        )
                        
                        if org.slack_webhook_url:
                            send_slack_alert(org.slack_webhook_url, alert_text)
                        if org.teams_webhook_url:
                            send_teams_alert(org.teams_webhook_url, alert_text)

        # STUCK WORKFLOW DETECTION
        check_stuck_workflows(db, now)
        
        # RUNTIME ANOMALY DETECTION (checked after runs complete)
        check_runtime_anomalies(db, now)

    finally:
        db.close()


def start_scheduler():
    """
    Start the APScheduler and register the periodic job.
    """
    scheduler.add_job(
        check_scheduled_workflows,
        "interval",
        minutes=1,
        id="check_scheduled_workflows",
        replace_existing=True,
    )
    scheduler.start()
    print("[monitor] APScheduler started")


def shutdown_scheduler():
    """
    Shutdown the scheduler on app shutdown.
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[monitor] APScheduler stopped")



def send_slack_alert(webhook_url: str, text: str):
    try:
        resp = httpx.post(webhook_url, json={"text": text})
        if resp.status_code >= 300:
            print(f"[monitor] Slack webhook error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[monitor] Slack webhook exception: {e}")


def send_teams_alert(webhook_url: str, text: str):
    """
    Send alert to Microsoft Teams using Adaptive Cards format.
    Teams requires a different JSON structure than Slack.
    """
    try:
        # Teams uses Adaptive Cards format
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": "CronWatch Alert",
            "themeColor": "FF6B35",  # Orange for warnings
            "title": "⚠️ Missed GitHub Actions Run",
            "text": text.replace("\n", "\n\n"),  # Teams uses double newlines for paragraphs
        }
        resp = httpx.post(webhook_url, json=card)
        if resp.status_code >= 300:
            print(f"[monitor] Teams webhook error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[monitor] Teams webhook exception: {e}")
