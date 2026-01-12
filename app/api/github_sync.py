from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.github_sync import discover_and_sync_workflows
from app.api.auth import get_current_user
import httpx
from app.api.auth import get_me  # Reuse get_me logic or just fetch installations here

router = APIRouter()


@router.post("/sync-workflows")
async def sync_workflows(
    db: Session = Depends(get_db),
    user_info = Depends(get_current_user)
):
    """
    Trigger a full discovery and sync of workflows for the authenticated user's installations.
    """
    # 1. Fetch user's installations to know what to sync
    # We can reuse the logic from get_me, or simpler: just fetch from GitHub API again
    token = user_info["token"]
    try:
        installations_response = httpx.get(
            "https://api.github.com/user/installations",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json"
            },
            timeout=10.0
        )
        if installations_response.status_code != 200:
             raise HTTPException(status_code=500, detail="Failed to fetch installations")
        
        installations_data = installations_response.json()
        installation_ids = [inst.get("id") for inst in installations_data.get("installations", [])]
        
        # 2. Run Discovery
        stats = discover_and_sync_workflows(db, installation_ids)
        
    except Exception as e:
        print(f"Sync failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    return stats
