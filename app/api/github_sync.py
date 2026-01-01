from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.github_sync import sync_cron_expressions

router = APIRouter()


@router.post("/sync-workflows")
def sync_workflows(db: Session = Depends(get_db)):
    try:
        sync_cron_expressions(db)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    return {"status": "ok"}
