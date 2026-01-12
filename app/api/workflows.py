# app/api/workflows.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.workflow import Workflow
from app.models.workflow_run import WorkflowRun
from app.schemas.workflow import WorkflowSummary
from app.schemas.workflow_run import WorkflowRunSchema

router = APIRouter()


from app.api.auth import get_current_user

# ...

@router.get("/", response_model=List[WorkflowSummary])
def list_workflows(
    db: Session = Depends(get_db),
    user_info = Depends(get_current_user)
):
    workflows = db.query(Workflow).all()
    result: list[WorkflowSummary] = []

    for wf in workflows:
        result.append(
            WorkflowSummary(
                id=wf.id,
                name=wf.name,
                repo_full_name=wf.repository.full_name if wf.repository else "",
                cron_expression=wf.cron_expression,
                last_run_at=wf.last_run_at,
            )
        )

    return result


@router.get("/{workflow_id}", response_model=WorkflowSummary)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    wf = db.query(Workflow).get(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return WorkflowSummary(
        id=wf.id,
        name=wf.name,
        repo_full_name=wf.repository.full_name if wf.repository else "",
        cron_expression=wf.cron_expression,
        last_run_at=wf.last_run_at,
    )


@router.get("/{workflow_id}/runs", response_model=List[WorkflowRunSchema])
def list_workflow_runs(
    workflow_id: int,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    # ensure workflow exists (optional but nicer errors)
    exists = db.query(Workflow).get(workflow_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Workflow not found")

    runs = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.workflow_id == workflow_id)
        .order_by(WorkflowRun.started_at.desc())
        .limit(limit)
        .all()
    )
    return runs

