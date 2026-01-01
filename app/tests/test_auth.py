from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.models.workflow import Organization

def test_login_redirect(client):
    response = client.get("/api/auth/login", follow_redirects=False)
    assert response.status_code == 307
    assert "github.com/login/oauth/authorize" in response.headers["location"]

def test_get_me_success(client, db):
    # Mock GitHub API responses
    mock_user_data = {
        "id": 12345,
        "login": "testuser",
        "avatar_url": "https://example.com/avatar.png",
        "name": "Test User"
    }
    
    mock_installations_data = {
        "installations": [
            {
                "id": 98765,
                "account": {
                    "id": 55555,
                    "login": "testorg",
                    "avatar_url": "https://example.com/org.png"
                }
            }
        ]
    }

    with patch("httpx.get") as mock_get:
        # Setup mock side effects for multiple calls
        def side_effect(url, headers, timeout):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if url == "https://api.github.com/user":
                mock_resp.json.return_value = mock_user_data
            elif url == "https://api.github.com/user/installations":
                mock_resp.json.return_value = mock_installations_data
            return mock_resp

        mock_get.side_effect = side_effect

        # Make request
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer fake-token"}
        )

        assert response.status_code == 200
        data = response.json()
        
        # Verify user data
        assert data["user"]["id"] == 12345
        assert data["user"]["login"] == "testuser"
        
        # Verify installation data
        assert len(data["installations"]) == 1
        assert data["installations"][0]["id"] == 98765
        assert data["installations"][0]["account_login"] == "testorg"
        
        # Verify DB side effect (Organization created)
        org = db.query(Organization).filter_by(installation_id=98765).first()
        assert org is not None
        assert org.name == "testorg"

def test_get_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
