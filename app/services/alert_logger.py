from datetime import datetime
from sqlalchemy.orm import Session
from app.models.alert import Alert, AlertType, AlertSeverity


def create_alert(
    db: Session,
    organization_id: int,
    alert_type: AlertType,
    message: str,
    workflow_id: int | None = None,
    severity: AlertSeverity = AlertSeverity.WARNING
) -> Alert:
    """
    Create and store an alert in the database.
    """
    alert = Alert(
        organization_id=organization_id,
        workflow_id=workflow_id,
        alert_type=alert_type,
        severity=severity,
        message=message,
        detected_at=datetime.utcnow()
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
