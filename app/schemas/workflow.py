from datetime import datetime
from pydantic import BaseModel, ConfigDict


class WorkflowSummary(BaseModel):
    id: int
    name: str
    repo_full_name: str
    cron_expression: str | None = None
    last_run_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

