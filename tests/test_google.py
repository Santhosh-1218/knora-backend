import pytest
from app.repositories.user_repository import user_repository

@pytest.mark.asyncio
async def test_google_login_url(async_client):
    res = await async_client.get("/api/auth/google/login")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "auth_url" in data["data"]
    assert "accounts.google.com" in data["data"]["auth_url"] or "mock_code" in data["data"]["auth_url"]


@pytest.mark.asyncio
async def test_google_callback_new_user(async_client):
    # Mock code triggers mock dev Google OAuth mode
    res = await async_client.get("/api/auth/google/callback?code=mock_code_sub_999&redirect=false")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["email"] == "mock_google_user@example.com"

    # Verify user saved in DB with google sub
    user = await user_repository.find_by_google_sub("sub_999")
    assert user is not None
    assert user.google.sub == "sub_999"
    assert "google" in user.auth_methods


@pytest.mark.asyncio
async def test_google_callback_account_linking(async_client):
    # Create existing user with email "mock_google_user@example.com"
    signup_payload = {
        "full_name": "Existing Knora User",
        "email": "mock_google_user@example.com",
        "mobile": "+919876543299",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    await async_client.post("/api/auth/signup", json=signup_payload)
    user = await user_repository.find_by_email("mock_google_user@example.com")
    await user_repository.update_user(str(user.id), {"status": "active"})

    # Now login with Google matching same email
    res = await async_client.get("/api/auth/google/callback?code=mock_code_sub_linked_888&redirect=false")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    
    # Check that Google sub was linked to the SAME user record (no duplicate user created!)
    updated_user = await user_repository.find_by_email("mock_google_user@example.com")
    assert updated_user.id == user.id
    assert updated_user.google.sub == "sub_linked_888"
    assert "google" in updated_user.auth_methods
    assert "password" in updated_user.auth_methods
