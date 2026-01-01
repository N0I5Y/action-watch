from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    github_run_id: Mapped[int] = mapped_column(Integer, index=True, unique=True)

    workflow_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflows.id", ondelete="CASCADE"), index=True
    )

    status: Mapped[str] = mapped_column(String(50), nullable=False)
    conclusion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)

    raw_payload: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    workflow = relationship("Workflow", back_populates="runs")

