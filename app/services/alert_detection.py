from sqlalchemy import func
from app.models.workflow_run import WorkflowRun
from app.services.alert_logger import create_alert
from app.models.alert import AlertType, AlertSeverity
from datetime import timedelta


def check_stuck_workflows(db, now):
    """
    Check for workflows that are currently running longer than expected.
    Alert if runtime > average_runtime * stuck_threshold_multiplier
    """
    from app.models.workflow import Workflow, Repository, Organization
    from app.services.scheduling import send_slack_alert, send_teams_alert
    
    # Get all running workflows (status = 'in_progress' or 'queued')
    running_runs = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.status.in_(['in_progress', 'queued']))
        .filter(WorkflowRun.started_at.isnot(None))
        .all()
    )
    
    for run in running_runs:
        workflow = db.query(Workflow).filter(Workflow.id == run.workflow_id).first()
        if not workflow or not workflow.repository or not workflow.repository.organization:
            continue
        
        org = workflow.repository.organization
        if not org.alert_on_stuck:
            continue
        
        # Calculate current runtime
        current_runtime_seconds = (now - run.started_at).total_seconds()
        
        # Get average runtime from historical completed runs
        avg_runtime = (
            db.query(func.avg(WorkflowRun.duration_ms))
            .filter(WorkflowRun.workflow_id == workflow.id)
            .filter(WorkflowRun.duration_ms.isnot(None))
            .filter(WorkflowRun.status == 'completed')
            .scalar()
        )
        
        if not avg_runtime or avg_runtime == 0:
            continue  # No historical data
        
        avg_runtime_seconds = avg_runtime / 1000
        threshold_seconds = avg_runtime_seconds * org.stuck_threshold_multiplier
        
        if current_runtime_seconds > threshold_seconds:
            alert_text = (
                f"🔄 *Stuck Workflow Detected*\n"
                f"Workflow: `{workflow.name}`\n"
                f"Repository: `{workflow.repository.full_name}`\n"
                f"Run ID: #{run.github_run_id}\n"
                f"Running for: {int(current_runtime_seconds / 60)} minutes\n"
                f"Average runtime: {int(avg_runtime_seconds / 60)} minutes\n"
                f"Threshold: {int(threshold_seconds / 60)} minutes ({org.stuck_threshold_multiplier}x avg)\n"
            )
            
            # Log to database
            create_alert(
                db=db,
                organization_id=org.id,
                workflow_id=workflow.id,
                alert_type=AlertType.STUCK,
                severity=AlertSeverity.WARNING,
                message=alert_text
            )
            
            if org.slack_webhook_url:
                send_slack_alert(org.slack_webhook_url, alert_text)
            if org.teams_webhook_url:
                send_teams_alert(org.teams_webhook_url, alert_text)


def check_runtime_anomalies(db, now):
    """
    Check recently completed runs for runtime anomalies.
    Alert if runtime > mean + (stddev * anomaly_threshold_stddev)
    """
    from app.models.workflow import Workflow, Repository, Organization
    from app.services.scheduling import send_slack_alert, send_teams_alert
    import math
    
    # Check runs completed in the last 5 minutes
    recent_cutoff = now - timedelta(minutes=5)
    
    recent_runs = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.completed_at >= recent_cutoff)
        .filter(WorkflowRun.duration_ms.isnot(None))
        .all()
    )
    
    for run in recent_runs:
        workflow = db.query(Workflow).filter(Workflow.id == run.workflow_id).first()
        if not workflow or not workflow.repository or not workflow.repository.organization:
            continue
        
        org = workflow.repository.organization
        if not org.alert_on_anomaly:
            continue
        
        # Get historical stats (mean and stddev)
        stats = (
            db.query(
                func.avg(WorkflowRun.duration_ms).label('mean'),
                func.stddev(WorkflowRun.duration_ms).label('stddev'),
                func.count().label('count')
            )
            .filter(WorkflowRun.workflow_id == workflow.id)
            .filter(WorkflowRun.duration_ms.isnot(None))
            .filter(WorkflowRun.id != run.id)  # Exclude current run
            .first()
        )
        
        if not stats.mean or not stats.stddev or stats.count < 5:
            continue  # Need at least 5 historical runs
        
        mean_ms = stats.mean
        stddev_ms = stats.stddev
        threshold_ms = mean_ms + (stddev_ms * org.anomaly_threshold_stddev)
        
        if run.duration_ms > threshold_ms:
            alert_text = (
                f"📈 *Runtime Anomaly Detected*\n"
                f"Workflow: `{workflow.name}`\n"
                f"Repository: `{workflow.repository.full_name}`\n"
                f"Run ID: #{run.github_run_id}\n"
                f"Duration: {int(run.duration_ms / 1000 / 60)} minutes\n"
                f"Average: {int(mean_ms / 1000 / 60)} minutes\n"
                f"Threshold: {int(threshold_ms / 1000 / 60)} minutes (mean + {org.anomaly_threshold_stddev}σ)\n"
                f"Deviation: {round((run.duration_ms - mean_ms) / stddev_ms, 2)}σ\n"
            )
            
            # Log to database
            create_alert(
                db=db,
                organization_id=org.id,
                workflow_id=workflow.id,
                alert_type=AlertType.ANOMALY,
                severity=AlertSeverity.WARNING,
                message=alert_text
            )
            
            if org.slack_webhook_url:
                send_slack_alert(org.slack_webhook_url, alert_text)
            if org.teams_webhook_url:
                send_teams_alert(org.teams_webhook_url, alert_text)
