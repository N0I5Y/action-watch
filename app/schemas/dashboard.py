# app/schemas/dashboard.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class WorkflowStatus(BaseModel):
    id: int
    repo_full_name: str
    name: str
    cron_expression: str | None = None
    last_run_at: datetime | None = None
    last_missed_at: datetime | None = None
    missed_count_24h: int
    status: str  # "HEALTHY" | "MISSED" | "AT_RISK"

    model_config = ConfigDict(from_attributes=True)


class SummaryStats(BaseModel):
    total_workflows: int
    healthy_workflows: int
    workflows_with_misses_24h: int
    last_missed_at: datetime | None = None
