from fastapi import APIRouter, Depends, HTTPException, Response, Header
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx
from pydantic import BaseModel

from app.core.config import settings
from app.core.db import get_db
from app.models.workflow import Organization

router = APIRouter()

class User(BaseModel):
    id: int
    login: str
    avatar_url: str
    name: str | None = None

class Installation(BaseModel):
    id: int
    account_login: str
    account_avatar_url: str

class AuthResponse(BaseModel):
    user: User
    installations: list[Installation]


def get_current_user(authorization: str | None = Header(None)):
    """Dependency to get current user from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    return {"token": token}


@router.get("/login")
async def login():
    """Redirect to GitHub OAuth."""
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&scope=read:user,read:org"
    )
    return RedirectResponse(url=github_auth_url)


@router.get("/callback")
async def callback(code: str, response: Response, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback."""
    # Exchange code for access token
    token_response = httpx.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GITHUB_REDIRECT_URI
        },
        timeout=10.0
    )
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get access token")
    
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")
    
    # Set cookie and redirect
    response.set_cookie(
        key="gh_token",
        value=access_token,
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=86400 * 30  # 30 days
    )
    
    # Redirect to frontend
    response.headers["Location"] = settings.FRONTEND_URL
    response.status_code = 302
    return response


@router.get("/me")
async def get_me(db: Session = Depends(get_db), user_info = Depends(get_current_user)):
    """Get current user info and their installations with subscription status."""
    from app.services.subscription import get_subscription_info
    
    token = user_info["token"]
    
    try:
        # Get user info
        user_response = httpx.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json"
            },
            timeout=10.0
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_data = user_response.json()
        
        # Get user's GitHub installations
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
        
        # Upsert organizations from installations
        installation_list = []
        for inst in installations_data.get("installations", []):
            account = inst.get("account", {})
            installation_id = inst.get("id")
            
            # Upsert organization
            org = db.query(Organization).filter(
                Organization.installation_id == installation_id
            ).first()
            
            if not org:
                org = Organization(
                    github_org_id=account.get("id"),
                    installation_id=installation_id,
                    name=account.get("login")
                )
                db.add(org)
                db.commit()
                db.refresh(org)
            
            # Get subscription info for this org
            subscription_info = get_subscription_info(org.id, db)
            
            installation_list.append({
                "id": installation_id,
                "account_login": account.get("login"),
                "account_avatar_url": account.get("avatar_url"),
                "subscription": subscription_info
            })
        
        return {
            "user": {
                "id": user_data["id"],
                "login": user_data["login"],
                "avatar_url": user_data["avatar_url"],
                "name": user_data.get("name")
            },
            "installations": installation_list
        }
        
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="GitHub API timeout")
    except Exception as e:
        print(f"Error in get_me: {e}")
        raise HTTPException(status_code=500, detail=str(e))
