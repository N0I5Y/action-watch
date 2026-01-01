from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.db import get_db
from app.models.workflow import Organization
from app.api.auth import get_current_user

router = APIRouter()

class SettingsUpdate(BaseModel):
    slack_webhook_url: str | None = None
    teams_webhook_url: str | None = None
    alert_threshold_minutes: int | None = None
    alert_on_delayed: bool | None = None
    alert_on_stuck: bool | None = None
    alert_on_anomaly: bool | None = None
    stuck_threshold_multiplier: float | None = None
    anomaly_threshold_stddev: float | None = None

class SettingsResponse(BaseModel):
    slack_webhook_url: str | None
    teams_webhook_url: str | None
    alert_threshold_minutes: int
    alert_on_delayed: bool
    alert_on_stuck: bool
    alert_on_anomaly: bool
    stuck_threshold_multiplier: float
    anomaly_threshold_stddev: float

@router.get("/{installation_id}", response_model=SettingsResponse)
async def get_settings(installation_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    # Verify user has access to this installation (TODO: strict check against user's installations)
    # For now, we trust the auth token is valid and the user is part of the org
    
    org = db.query(Organization).filter(Organization.installation_id == installation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return SettingsResponse(
        slack_webhook_url=org.slack_webhook_url,
        teams_webhook_url=org.teams_webhook_url,
        alert_threshold_minutes=org.alert_threshold_minutes or 10,
        alert_on_delayed=org.alert_on_delayed if org.alert_on_delayed is not None else True,
        alert_on_stuck=org.alert_on_stuck if org.alert_on_stuck is not None else True,
        alert_on_anomaly=org.alert_on_anomaly if org.alert_on_anomaly is not None else True,
        stuck_threshold_multiplier=org.stuck_threshold_multiplier or 2.0,
        anomaly_threshold_stddev=org.anomaly_threshold_stddev or 2.0
    )

@router.patch("/{installation_id}", response_model=SettingsResponse)
async def update_settings(installation_id: int, settings: SettingsUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    org = db.query(Organization).filter(Organization.installation_id == installation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if settings.slack_webhook_url is not None:
        org.slack_webhook_url = settings.slack_webhook_url
    
    if settings.teams_webhook_url is not None:
        org.teams_webhook_url = settings.teams_webhook_url
    
    if settings.alert_threshold_minutes is not None:
        org.alert_threshold_minutes = settings.alert_threshold_minutes
    
    if settings.alert_on_delayed is not None:
        org.alert_on_delayed = settings.alert_on_delayed
    
    if settings.alert_on_stuck is not None:
        org.alert_on_stuck = settings.alert_on_stuck
    
    if settings.alert_on_anomaly is not None:
        org.alert_on_anomaly = settings.alert_on_anomaly
    
    if settings.stuck_threshold_multiplier is not None:
        org.stuck_threshold_multiplier = settings.stuck_threshold_multiplier
    
    if settings.anomaly_threshold_stddev is not None:
        org.anomaly_threshold_stddev = settings.anomaly_threshold_stddev
        
    db.commit()
    db.refresh(org)
    
    return SettingsResponse(
        slack_webhook_url=org.slack_webhook_url,
        teams_webhook_url=org.teams_webhook_url,
        alert_threshold_minutes=org.alert_threshold_minutes or 10,
        alert_on_delayed=org.alert_on_delayed if org.alert_on_delayed is not None else True,
        alert_on_stuck=org.alert_on_stuck if org.alert_on_stuck is not None else True,
        alert_on_anomaly=org.alert_on_anomaly if org.alert_on_anomaly is not None else True,
        stuck_threshold_multiplier=org.stuck_threshold_multiplier or 2.0,
        anomaly_threshold_stddev=org.anomaly_threshold_stddev or 2.0
    )
