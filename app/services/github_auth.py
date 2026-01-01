import time
import jwt
import httpx
from app.core.config import get_settings

settings = get_settings()

def get_jwt() -> str:
    """
    Generate a JWT for the GitHub App.
    """
    if settings.GITHUB_APP_PRIVATE_KEY:
        private_key = settings.GITHUB_APP_PRIVATE_KEY
    elif settings.GITHUB_APP_PRIVATE_KEY_PATH:
        with open(settings.GITHUB_APP_PRIVATE_KEY_PATH, "r") as f:
            private_key = f.read()
    else:
        raise RuntimeError("No GitHub App private key found (env or path)")

    if not settings.GITHUB_APP_ID:
        raise RuntimeError("GITHUB_APP_ID not set")

    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": settings.GITHUB_APP_ID,
    }

    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    return encoded_jwt


def get_installation_token(installation_id: int) -> str:
    """
    Get an access token for a specific installation.
    """
    jwt_token = get_jwt()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }
    
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    
    with httpx.Client() as client:
        resp = client.post(url, headers=headers)
        if resp.status_code != 201:
            raise RuntimeError(f"Failed to get installation token: {resp.status_code} {resp.text}")
        
        data = resp.json()
        return data["token"]
