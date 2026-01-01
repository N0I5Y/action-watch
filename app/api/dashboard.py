# app/api/dashboard.py
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.workflow import Workflow
from app.models.workflow_run import WorkflowRun
from app.schemas.dashboard import WorkflowStatus, SummaryStats

router = APIRouter()


def compute_status(
    wf: Workflow,
    now: datetime,
    missed_runs: list[WorkflowRun],
) -> WorkflowStatus:
    last_run_at = wf.last_run_at
    last_missed_at = (
        missed_runs[0].started_at if missed_runs else None
    )  # assuming started_at ~ expected time

    # Simple status logic for now:
    if last_missed_at:
        status = "MISSED"
    else:
        status = "HEALTHY"

    return WorkflowStatus(
        id=wf.id,
        repo_full_name=wf.repository.full_name if wf.repository else "",
        name=wf.name,
        cron_expression=wf.cron_expression,
        last_run_at=last_run_at,
        last_missed_at=last_missed_at,
        missed_count_24h=len(missed_runs),
        status=status,
    )


@router.get("/workflows/status", response_model=List[WorkflowStatus])
def list_workflows_status(
    q: str | None = Query(None, description="Search by repo or workflow name"),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    since_24h = now - timedelta(hours=24)

    query = db.query(Workflow).join(Workflow.repository)

    if q:
        like = f"%{q}%"
        query = query.filter(
            (Workflow.name.ilike(like))
            | (WorkflowRepository.full_name.ilike(like))  # type: ignore
        )

    workflows: list[Workflow] = query.all()
    items: list[WorkflowStatus] = []

    for wf in workflows:
        missed_runs = (
            db.query(WorkflowRun)
            .filter(WorkflowRun.workflow_id == wf.id)
            .filter(WorkflowRun.conclusion == "missed")  # if you store misses this way
            .filter(WorkflowRun.started_at >= since_24h)
            .order_by(WorkflowRun.started_at.desc())
            .all()
        )

        items.append(compute_status(wf, now, missed_runs))

    return items


@router.get("/summary", response_model=SummaryStats)
def get_summary(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    since_24h = now - timedelta(hours=24)

    total_workflows = db.query(Workflow).count()

    # crude approximation: consider “healthy” those without any misses in last 24h
    workflows_with_misses = (
        db.query(WorkflowRun.workflow_id)
        .filter(WorkflowRun.conclusion == "missed")
        .filter(WorkflowRun.started_at >= since_24h)
        .distinct()
        .all()
    )
    workflows_with_misses_ids = {row[0] for row in workflows_with_misses}
    healthy_workflows = total_workflows - len(workflows_with_misses_ids)

    last_missed = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.conclusion == "missed")
        .order_by(WorkflowRun.started_at.desc())
        .first()
    )
    last_missed_at = last_missed.started_at if last_missed else None

    return SummaryStats(
        total_workflows=total_workflows,
        healthy_workflows=healthy_workflows,
        workflows_with_misses_24h=len(workflows_with_misses_ids),
        last_missed_at=last_missed_at,
    )


@router.get("/workflows/{workflow_id}/runs")
def get_workflow_runs(
    workflow_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    runs = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.workflow_id == workflow_id)
        .order_by(WorkflowRun.started_at.desc())
        .limit(limit)
        .all()
    )
    # simple raw dicts for now
    return {
        "workflow_id": workflow_id,
        "runs": [
            {
                "id": r.id,
                "status": r.status,
                "conclusion": r.conclusion,
                "started_at": r.started_at,
                "completed_at": r.completed_at,
                "duration_ms": r.duration_ms,
            }
            for r in runs
        ],
    }
