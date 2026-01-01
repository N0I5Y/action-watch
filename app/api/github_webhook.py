from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.db import get_db
from app.models.workflow import Organization, Repository, Workflow
from app.models.workflow_run import WorkflowRun


router = APIRouter()


@router.post("/webhook")
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    # TODO: verify signature using GITHUB_WEBHOOK_SECRET
    event = request.headers.get("X-GitHub-Event")
    payload = await request.json()

    if event == "installation":
        return await handle_installation(payload, db)
    elif event == "installation_repositories":
        return await handle_installation_repositories(payload, db)
    elif event == "workflow_run":
        return await handle_workflow_run(payload, db)
    
    return {"status": "ignored", "reason": "unsupported_event"}


async def handle_installation(payload: dict, db: Session):
    action = payload.get("action")
    installation = payload.get("installation")
    account = installation.get("account")
    
    if not installation or not account:
        return {"status": "error", "message": "Invalid payload"}

    github_org_id = account.get("id")
    installation_id = installation.get("id")
    name = account.get("login")

    if action in ["created", "new_permissions_accepted"]:
        # Upsert Organization
        org = db.query(Organization).filter(Organization.github_org_id == github_org_id).one_or_none()
        if not org:
            org = Organization(
                github_org_id=github_org_id,
                installation_id=installation_id,
                name=name
            )
            db.add(org)
        else:
            org.installation_id = installation_id
            org.name = name
        
        db.commit()
        
        # If repositories are included in the payload (sometimes in 'repositories' key)
        if "repositories" in payload:
            for repo_data in payload["repositories"]:
                await upsert_repo(repo_data, org, db)

    elif action == "deleted":
        # Remove organization and its data
        # In a real app, you might want to soft-delete or keep data for a while
        org = db.query(Organization).filter(Organization.github_org_id == github_org_id).one_or_none()
        if org:
            db.delete(org)
            db.commit()
    
    return {"status": "ok"}


async def handle_installation_repositories(payload: dict, db: Session):
    action = payload.get("action")
    installation = payload.get("installation")
    
    if not installation:
        return {"status": "error", "message": "No installation in payload"}

    installation_id = installation.get("id")
    org = db.query(Organization).filter(Organization.installation_id == installation_id).first()
    
    if not org:
        # Should have been created by installation event, but maybe we missed it
        # Can try to fetch from payload if available, or ignore
        return {"status": "ignored", "reason": "organization_not_found"}

    if action == "added":
        for repo_data in payload.get("repositories_added", []):
            await upsert_repo(repo_data, org, db)
            
    elif action == "removed":
        for repo_data in payload.get("repositories_removed", []):
            repo = db.query(Repository).filter(Repository.github_repo_id == repo_data["id"]).one_or_none()
            if repo:
                db.delete(repo)
        db.commit()

    return {"status": "ok"}


async def upsert_repo(repo_data: dict, org: Organization, db: Session):
    repo = db.query(Repository).filter(Repository.github_repo_id == repo_data["id"]).one_or_none()
    if not repo:
        repo = Repository(
            github_repo_id=repo_data["id"],
            org_id=org.id,
            name=repo_data["name"],
            full_name=repo_data["full_name"],
        )
        db.add(repo)
    else:
        repo.name = repo_data["name"]
        repo.full_name = repo_data["full_name"]
        repo.org_id = org.id
    db.commit()


async def handle_workflow_run(payload: dict, db: Session):
    workflow_run = payload.get("workflow_run")
    repo_payload = payload.get("repository")
    installation = payload.get("installation")
    
    if not workflow_run or not repo_payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workflow_run payload",
        )

    # Ensure Organization exists (if we missed installation event)
    # We can try to find by installation_id if present, or fallback to owner id
    org_payload = payload.get("organization") or repo_payload.get("owner")
    github_org_id = org_payload.get("id")
    
    org = db.query(Organization).filter(Organization.github_org_id == github_org_id).one_or_none()
    if not org:
        # Create on the fly
        org = Organization(
            github_org_id=github_org_id,
            name=org_payload.get("login"),
            installation_id=installation.get("id") if installation else None
        )
        db.add(org)
        db.flush()
    else:
        # Update installation_id if missing
        if installation and not org.installation_id:
            org.installation_id = installation["id"]
            db.flush()

    # Upsert repository
    github_repo_id = repo_payload["id"]
    repo = (
        db.query(Repository)
        .filter(Repository.github_repo_id == github_repo_id)
        .one_or_none()
    )
    if not repo:
        repo = Repository(
            github_repo_id=github_repo_id,
            org_id=org.id,
            name=repo_payload["name"],
            full_name=repo_payload["full_name"],
        )
        db.add(repo)
        db.flush()

    # Upsert workflow
    github_workflow_id = workflow_run["workflow_id"]
    workflow = (
        db.query(Workflow)
        .filter(Workflow.github_workflow_id == github_workflow_id)
        .one_or_none()
    )
    if not workflow:
        workflow = Workflow(
            github_workflow_id=github_workflow_id,
            repo_id=repo.id,
            name=workflow_run["name"],
            path=workflow_run.get("path") or "",
        )
        db.add(workflow)
        db.flush()

    # Create or update workflow run
    github_run_id = workflow_run["id"]
    run = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.github_run_id == github_run_id)
        .one_or_none()
    )

    started_at = (
        datetime.fromisoformat(workflow_run["run_started_at"].replace("Z", "+00:00"))
        if workflow_run.get("run_started_at")
        else datetime.utcnow()
    )
    completed_at = (
        datetime.fromisoformat(workflow_run["updated_at"].replace("Z", "+00:00"))
        if workflow_run.get("updated_at")
        else None
    )

    duration_ms = None
    if completed_at:
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)

    if not run:
        run = WorkflowRun(
            github_run_id=github_run_id,
            workflow_id=workflow.id,
            status=workflow_run["status"],
            conclusion=workflow_run.get("conclusion"),
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            raw_payload=str(payload),
        )
        db.add(run)
    else:
        run.status = workflow_run["status"]
        run.conclusion = workflow_run.get("conclusion")
        run.started_at = started_at
        run.completed_at = completed_at
        run.duration_ms = duration_ms
        run.raw_payload = str(payload)

    # Update workflow last_run_at
    workflow.last_run_at = completed_at or started_at

    db.commit()

    return {"status": "ok"}
