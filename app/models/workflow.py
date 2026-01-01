from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    BigInteger,
    Float,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.db import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    github_org_id = Column(BigInteger, unique=True, index=True, nullable=False)
    installation_id = Column(BigInteger, index=True, nullable=True)
    name = Column(String, nullable=False)
    slack_webhook_url = Column(String, nullable=True)
    teams_webhook_url = Column(String, nullable=True)
    alert_threshold_minutes = Column(Integer, default=10) # Default 10 mins grace
    
    # Advanced alert type settings
    alert_on_delayed = Column(Boolean, default=True)
    alert_on_stuck = Column(Boolean, default=True)
    alert_on_anomaly = Column(Boolean, default=True)
    stuck_threshold_multiplier = Column(Float, default=2.0)  # Alert if runtime > avg * 2
    anomaly_threshold_stddev = Column(Float, default=2.0)  # Alert if runtime > avg + 2*stddev

    repositories = relationship("Repository", back_populates="organization")


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    github_repo_id = Column(BigInteger, unique=True, index=True, nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)  # org/name

    organization = relationship("Organization", back_populates="repositories")
    workflows = relationship("Workflow", back_populates="repository")


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    github_workflow_id = Column(BigInteger, unique=True, index=True, nullable=False)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)  # .github/workflows/file.yml

    cron_expression = Column(String, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)

    repository = relationship("Repository", back_populates="workflows")
    runs = relationship("app.models.workflow_run.WorkflowRun", back_populates="workflow",cascade="all, delete-orphan")

