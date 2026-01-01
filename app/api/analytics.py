from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from typing import List

from app.core.db import get_db
from app.models.workflow_run import WorkflowRun
from app.models.workflow import Workflow, Repository, Organization
from app.api.auth import get_current_user
from app.services.subscription import is_pro_user

router = APIRouter()

class SuccessRateDataPoint(BaseModel):
    date: str
    success: int
    failure: int
    total: int

class RuntimeTrendDataPoint(BaseModel):
    date: str
    avg_duration_seconds: float
    run_count: int

class DurationStats(BaseModel):
    min_duration_ms: int | None
    max_duration_ms: int | None
    avg_duration_ms: float | None
    p50_duration_ms: float | None
    p95_duration_ms: float | None
    total_runs: int

@router.get("/success-rate", response_model=List[SuccessRateDataPoint])
async def get_success_rate(
    installation_id: int = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Get success/failure rate over time for workflows in an installation."""
    org = db.query(Organization).filter(Organization.installation_id == installation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if user has Pro subscription
    if not is_pro_user(org.id, db):
        raise HTTPException(
            status_code=403, 
            detail="Analytics requires a Pro subscription. Upgrade to unlock this feature."
        )
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get all workflows for this installation
    workflows = (
        db.query(Workflow.id)
        .join(Repository)
        .join(Organization)
        .filter(Organization.installation_id == installation_id)
        .subquery()
    )
    
    # Query runs grouped by date
    results = (
        db.query(
            func.date(WorkflowRun.started_at).label("date"),
            func.count().filter(WorkflowRun.conclusion == "success").label("success"),
            func.count().filter(WorkflowRun.conclusion == "failure").label("failure"),
            func.count().label("total")
        )
        .filter(
            and_(
                WorkflowRun.workflow_id.in_(workflows),
                WorkflowRun.started_at >= start_date
            )
        )
        .group_by(func.date(WorkflowRun.started_at))
        .order_by(func.date(WorkflowRun.started_at))
        .all()
    )
    
    return [
        SuccessRateDataPoint(
            date=str(row.date),
            success=row.success or 0,
            failure=row.failure or 0,
            total=row.total
        )
        for row in results
    ]

@router.get("/runtime-trends", response_model=List[RuntimeTrendDataPoint])
async def get_runtime_trends(
    installation_id: int = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Get average runtime trends over time."""
    org = db.query(Organization).filter(Organization.installation_id == installation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if user has Pro subscription
    if not is_pro_user(org.id, db):
        raise HTTPException(
            status_code=403, 
            detail="Analytics requires a Pro subscription. Upgrade to unlock this feature."
        )
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    workflows = (
        db.query(Workflow.id)
        .join(Repository)
        .join(Organization)
        .filter(Organization.installation_id == installation_id)
        .subquery()
    )
    
    results = (
        db.query(
            func.date(WorkflowRun.started_at).label("date"),
            func.avg(WorkflowRun.duration_ms).label("avg_duration_ms"),
            func.count().label("run_count")
        )
        .filter(
            and_(
                WorkflowRun.workflow_id.in_(workflows),
                WorkflowRun.started_at >= start_date,
                WorkflowRun.duration_ms.isnot(None)
            )
        )
        .group_by(func.date(WorkflowRun.started_at))
        .order_by(func.date(WorkflowRun.started_at))
        .all()
    )
    
    return [
        RuntimeTrendDataPoint(
            date=str(row.date),
            avg_duration_seconds=round((row.avg_duration_ms or 0) / 1000, 2),
            run_count=row.run_count
        )
        for row in results
    ]

@router.get("/duration-stats", response_model=DurationStats)
async def get_duration_stats(
    installation_id: int = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Get duration statistics (min/max/avg/percentiles)."""
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    org = db.query(Organization).filter(Organization.installation_id == installation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if user has Pro subscription
    if not is_pro_user(org.id, db):
        raise HTTPException(
            status_code=403, 
            detail="Analytics requires a Pro subscription. Upgrade to unlock this feature."
        )
    
    workflows = (
        db.query(Workflow.id)
        .join(Repository)
        .join(Organization)
        .filter(Organization.installation_id == installation_id)
        .subquery()
    )
    
    # Get basic stats
    stats = (
        db.query(
            func.min(WorkflowRun.duration_ms).label("min_duration"),
            func.max(WorkflowRun.duration_ms).label("max_duration"),
            func.avg(WorkflowRun.duration_ms).label("avg_duration"),
            func.count().label("total_runs")
        )
        .filter(
            and_(
                WorkflowRun.workflow_id.in_(workflows),
                WorkflowRun.started_at >= start_date,
                WorkflowRun.duration_ms.isnot(None)
            )
        )
        .first()
    )
    
    # Get percentiles (p50, p95)
    # Note: PostgreSQL has percentile_cont, but for simplicity we'll approximate
    durations = (
        db.query(WorkflowRun.duration_ms)
        .filter(
            and_(
                WorkflowRun.workflow_id.in_(workflows),
                WorkflowRun.started_at >= start_date,
                WorkflowRun.duration_ms.isnot(None)
            )
        )
        .order_by(WorkflowRun.duration_ms)
        .all()
    )
    
    p50 = None
    p95 = None
    if durations:
        sorted_durations = [d[0] for d in durations]
        p50_idx = int(len(sorted_durations) * 0.5)
        p95_idx = int(len(sorted_durations) * 0.95)
        p50 = sorted_durations[p50_idx] if p50_idx < len(sorted_durations) else None
        p95 = sorted_durations[p95_idx] if p95_idx < len(sorted_durations) else None
    
    return DurationStats(
        min_duration_ms=stats.min_duration,
        max_duration_ms=stats.max_duration,
        avg_duration_ms=round(stats.avg_duration, 2) if stats.avg_duration else None,
        p50_duration_ms=p50,
        p95_duration_ms=p95,
        total_runs=stats.total_runs
    )
