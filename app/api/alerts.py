from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from pydantic import BaseModel
from typing import List

from app.core.db import get_db
from app.models.alert import Alert, AlertType, AlertSeverity
from app.models.workflow import Organization
from app.api.auth import get_current_user
from app.services.subscription import is_pro_user

router = APIRouter()


class AlertResponse(BaseModel):
    id: int
    workflow_id: int | None
    alert_type: str
    severity: str
    message: str
    detected_at: datetime
    acknowledged: bool
    acknowledged_at: datetime | None
    workflow_name: str | None
    repository_name: str | None

    class Config:
        from_attributes = True


class AcknowledgeRequest(BaseModel):
    acknowledged: bool


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    installation_id: int = Query(...),
    limit: int = Query(50, ge=1, le=200),
    alert_type: str | None = Query(None),
    acknowledged: bool | None = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Get alerts for an installation."""
    # Get organization
    org = db.query(Organization).filter(Organization.installation_id == installation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if user has Pro subscription
    if not is_pro_user(org.id, db):
        raise HTTPException(
            status_code=403, 
            detail="Alert History requires a Pro subscription. Upgrade to unlock this feature."
        )
    
    # Build query
    query = db.query(Alert).filter(Alert.organization_id == org.id)
    
    # Apply filters
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if acknowledged is not None:
        query = query.filter(Alert.acknowledged == acknowledged)
    
    # Order by most recent first
    query = query.order_by(desc(Alert.detected_at)).limit(limit)
    
    alerts = query.all()
    
    # Format response
    result = []
    for alert in alerts:
        workflow_name = None
        repository_name = None
        if alert.workflow:
            workflow_name = alert.workflow.name
            if alert.workflow.repository:
                repository_name = alert.workflow.repository.full_name
        
        result.append(AlertResponse(
            id=alert.id,
            workflow_id=alert.workflow_id,
            alert_type=alert.alert_type.value,
            severity=alert.severity.value,
            message=alert.message,
            detected_at=alert.detected_at,
            acknowledged=alert.acknowledged,
            acknowledged_at=alert.acknowledged_at,
            workflow_name=workflow_name,
            repository_name=repository_name
        ))
    
    return result


@router.patch("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    request: AcknowledgeRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Mark an alert as acknowledged."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = request.acknowledged
    alert.acknowledged_at = datetime.utcnow() if request.acknowledged else None
    
    db.commit()
    db.refresh(alert)
    
    return {"success": True, "acknowledged": alert.acknowledged}
