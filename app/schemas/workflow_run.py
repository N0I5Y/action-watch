from datetime import datetime
from pydantic import BaseModel


class WorkflowRunSchema(BaseModel):
    id: int
    github_run_id: int
    status: str
    conclusion: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None

    class Config:
        from_attributes = True  # pydantic v2 replacement for orm_mode = True
