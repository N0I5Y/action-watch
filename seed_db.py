import sys
import os
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.db import Base
from app.models.workflow import Organization, Repository, Workflow
from app.models.workflow_run import WorkflowRun

# Force SQLite
DATABASE_URL = "sqlite:///./dev.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed():
    # Create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Org
    org = Organization(
        github_org_id=12345,
        name="Acme Corp",
        installation_id=98765,
        alert_threshold_minutes=15
    )
    db.add(org)
    db.flush()
    
    # Repos
    repo1 = Repository(
        github_repo_id=111,
        org_id=org.id,
        name="backend-api",
        full_name="acme/backend-api"
    )
    repo2 = Repository(
        github_repo_id=222,
        org_id=org.id,
        name="frontend-web",
        full_name="acme/frontend-web"
    )
    db.add_all([repo1, repo2])
    db.flush()
    
    # Workflows
    wf1 = Workflow(
        github_workflow_id=1001,
        repo_id=repo1.id,
        name="Nightly Build",
        path=".github/workflows/nightly.yml",
        cron_expression="0 0 * * *",
        active=True,
        last_run_at=datetime.utcnow() - timedelta(hours=2),
        next_run_at=datetime.utcnow() + timedelta(hours=22)
    )
    
    wf2 = Workflow(
        github_workflow_id=1002,
        repo_id=repo1.id,
        name="Data Sync",
        path=".github/workflows/sync.yml",
        cron_expression="*/15 * * * *",
        active=True,
        last_run_at=datetime.utcnow() - timedelta(minutes=5),
        next_run_at=datetime.utcnow() + timedelta(minutes=10)
    )

    wf3 = Workflow(
        github_workflow_id=1003,
        repo_id=repo2.id,
        name="Deploy Staging",
        path=".github/workflows/deploy.yml",
        cron_expression="0 12 * * *",
        active=True,
        last_run_at=datetime.utcnow() - timedelta(days=1),
        next_run_at=datetime.utcnow() + timedelta(hours=5)
    )
    
    db.add_all([wf1, wf2, wf3])
    db.flush()
    
    # Runs (History)
    statuses = ["completed", "completed", "completed", "failure", "completed"]
    conclusions = ["success", "success", "success", "failure", "success"]
    
    for wf in [wf1, wf2, wf3]:
        for i in range(10):
            start = datetime.utcnow() - timedelta(days=i)
            end = start + timedelta(minutes=random.randint(2, 15))
            status = random.choice(statuses)
            conclusion = "success" if status == "completed" else "failure"
            
            run = WorkflowRun(
                workflow_id=wf.id,
                github_run_id=5000 + i + wf.id,
                run_number=100 - i,
                status=status,
                conclusion=conclusion,
                started_at=start,
                completed_at=end if status == "completed" else None,
                created_at=start
            )
            db.add(run)
            
    db.commit()
    print("Database seeded successfully with dummy data!")

if __name__ == "__main__":
    seed()
