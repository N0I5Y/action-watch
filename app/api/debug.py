from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.workflow import Workflow
from app.services.scheduling import check_scheduled_workflows

router = APIRouter()


@router.post("/force-missed/{workflow_id}")
def force_missed(workflow_id: int, db: Session = Depends(get_db)):
    """
    For dev only:
    - Set last_run_at far in the past
    - Invoke the monitor once
    """
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).one_or_none()
    if not wf:
        return {"status": "error", "message": "workflow not found"}

    # Set it to 1 day ago to guarantee it's "old"
    wf.last_run_at = datetime.now(timezone.utc) - timedelta(days=1)
    db.commit()

    # Run monitor once (synchronously)
    check_scheduled_workflows()

    return {
        "status": "ok",
        "message": "Forced last_run_at to yesterday and ran monitor once",
    }
