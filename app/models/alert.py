from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.db import Base


class AlertType(str, enum.Enum):
    MISSED = "missed"
    DELAYED = "delayed"
    STUCK = "stuck"
    ANOMALY = "anomaly"


class AlertSeverity(str, enum.Enum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False, default=AlertSeverity.WARNING)
    message = Column(Text, nullable=False)
    
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Relationships
    workflow = relationship("Workflow", backref="alerts")
    organization = relationship("Organization", backref="alerts")
