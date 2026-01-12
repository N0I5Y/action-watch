import base64
import json
from typing import Optional, Dict, List

import httpx
import yaml
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.workflow import Workflow
from app.services.github_auth import get_installation_token

settings = get_settings()


def fetch_workflow_file(owner: str, repo: str, path: str, token: str) -> Optional[str]:
    """
    Fetch workflow YAML content from GitHub using installation token.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    try:
        resp = httpx.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"[github_sync] Failed to fetch {owner}/{repo}/{path}: {resp.status_code} {resp.text}")
            return None

        data = resp.json()
        # Content is base64-encoded
        content_b64 = data.get("content")
        if not content_b64:
            return None

        decoded = base64.b64decode(content_b64).decode("utf-8")
        return decoded
    except Exception as e:
        print(f"[github_sync] Exception fetching file: {e}")
        return None


def extract_cron_from_yaml(yaml_content: str) -> Optional[str]:
    """
    Given YAML content of a workflow file, extract the first schedule cron expression.
    """
    try:
        parsed = yaml.safe_load(yaml_content)
    except Exception as e:
        print(f"[github_sync] YAML parse error: {e}")
        return None

    def find_cron(node) -> Optional[str]:
        # If it's a dict, look for 'schedule' key and recurse into values
        if isinstance(node, dict):
            # Direct schedule
            if "schedule" in node:
                schedule_block = node["schedule"]

                # schedule: [{cron: "..."}]
                if isinstance(schedule_block, list):
                    for item in schedule_block:
                        if isinstance(item, dict) and "cron" in item:
                            return item["cron"]

                # schedule: {cron: "..."} (less common)
                if isinstance(schedule_block, dict) and "cron" in schedule_block:
                    return schedule_block["cron"]

            # Recurse into all values
            for value in node.values():
                cron = find_cron(value)
                if cron:
                    return cron

        # If it's a list, recurse into each element
        if isinstance(node, list):
            for item in node:
                cron = find_cron(item)
                if cron:
                    return cron

        return None

    cron_value = find_cron(parsed)
    if not cron_value:
        print("[github_sync] No schedule/cron found in YAML structure")
    return cron_value


def sync_cron_expressions(db: Session):
    """
    For each workflow in DB, fetch its YAML, parse cron, and update cron_expression.
    Uses installation tokens.
    """
    workflows = db.query(Workflow).all()
    print(f"[github_sync] Found {len(workflows)} workflows to sync")

    # Group workflows by installation_id to minimize token fetches
    workflows_by_installation: Dict[int, List[Workflow]] = {}
    
    for wf in workflows:
        if not wf.repository or not wf.repository.organization:
            continue
            
        installation_id = wf.repository.organization.installation_id
        if not installation_id:
            print(f"[github_sync] Skipping workflow {wf.id} (no installation_id)")
            continue
            
        if installation_id not in workflows_by_installation:
            workflows_by_installation[installation_id] = []
        workflows_by_installation[installation_id].append(wf)

    for installation_id, installation_workflows in workflows_by_installation.items():
        print(f"[github_sync] Processing installation {installation_id} ({len(installation_workflows)} workflows)")
        
        try:
            token = get_installation_token(installation_id)
        except Exception as e:
            print(f"[github_sync] Failed to get token for installation {installation_id}: {e}")
            continue

        for wf in installation_workflows:
            if not wf.path:
                continue

            owner, repo = wf.repository.full_name.split("/", 1)
            print(f"[github_sync] Syncing {owner}/{repo}/{wf.path}")

            yaml_content = fetch_workflow_file(owner, repo, wf.path, token)
            if not yaml_content:
                continue

            cron = extract_cron_from_yaml(yaml_content)
            if cron:
                print(f"[github_sync] Workflow {wf.id} cron: {cron}")
                wf.cron_expression = cron
            else:
                print(f"[github_sync] No cron found for workflow {wf.id}")
                # Optional: clear cron if removed? 
                # wf.cron_expression = None 

    db.commit()
    print("[github_sync] Sync complete")



def discover_and_sync_workflows(db: Session, user_installations: List[int]) -> Dict:
    """
    Discover repos and workflows for the given installation IDs and sync to DB.
    Returns a summary dict for debugging.
    """
    import httpx
    from app.services.github_auth import get_installation_token
    from app.models.workflow import Organization, Repository, Workflow
    
    stats = {
        "installations_processed": 0,
        "repos_found": 0,
        "workflows_found": 0,
        "errors": []
    }

    for installation_id in user_installations:
        try:
            token = get_installation_token(installation_id)
        except Exception as e:
            msg = f"Failed to get token for inst {installation_id}: {e}"
            print(f"[github_sync] {msg}")
            stats["errors"].append(msg)
            continue
        
        stats["installations_processed"] += 1

        # 1. Get Installation Repos
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        repos_resp = httpx.get(
            "https://api.github.com/installation/repositories?per_page=100", 
            headers=headers
        )
        if repos_resp.status_code != 200:
            msg = f"Failed to fetch repos for inst {installation_id}: {repos_resp.status_code} {repos_resp.text}"
            print(f"[github_sync] {msg}")
            stats["errors"].append(msg)
            continue
            
        repos_data = repos_resp.json().get("repositories", [])
        stats["repos_found"] += len(repos_data)
        
        # 2. Process Repos
        for repo_data in repos_data:
            owner_login = repo_data["owner"]["login"]
            repo_name = repo_data["name"]
            full_name = repo_data["full_name"]
            github_repo_id = repo_data["id"]

            try:
                # Ensure Org exists
                org_github_id = repo_data["owner"]["id"]
                org = db.query(Organization).filter(Organization.github_org_id == org_github_id).first()
                if not org:
                    org = Organization(
                        github_org_id=org_github_id,
                        installation_id=installation_id,
                        name=owner_login
                    )
                    db.add(org)
                    db.flush() 

                # Ensure Repo exists
                repo = db.query(Repository).filter(Repository.github_repo_id == github_repo_id).first()
                if not repo:
                    repo = Repository(
                        github_repo_id=github_repo_id,
                        org_id=org.id,
                        name=repo_name,
                        full_name=full_name
                    )
                    db.add(repo)
                    db.flush()

                # 3. Get Workflows for Repo
                wf_resp = httpx.get(
                    f"https://api.github.com/repos/{full_name}/actions/workflows",
                    headers=headers
                )
                if wf_resp.status_code != 200:
                    stats["errors"].append(f"Failed to fetch workflows for {full_name}: {wf_resp.status_code}")
                    continue
                    
                wfs_data = wf_resp.json().get("workflows", [])
                stats["workflows_found"] += len(wfs_data)

                for wf_data in wfs_data:
                    github_wf_id = wf_data["id"]
                    wf_name = wf_data["name"]
                    wf_path = wf_data["path"]
                    
                # Upsert Workflow
                wf = db.query(Workflow).filter(Workflow.github_workflow_id == github_wf_id).first()
                if not wf:
                    wf = Workflow(
                        github_workflow_id=github_wf_id,
                        repo_id=repo.id,
                        name=wf_name,
                        path=wf_path,
                        # state=wf_data["state"],  <-- REMOVED
                        active=(wf_data["state"] == "active")
                    )
                    db.add(wf)
                else:
                    wf.name = wf_name
                    wf.path = wf_path
                    # wf.state = wf_data["state"] <-- REMOVED
                    wf.active = (wf_data["state"] == "active")
                        
            except Exception as inner_e:
                stats["errors"].append(f"Error processing repo {full_name}: {inner_e}")
                continue

        db.commit()
    
    # After discovery, run strict cron sync to update cron_expressions
    sync_cron_expressions(db)
    
    return stats
