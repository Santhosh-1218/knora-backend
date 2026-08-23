import pytest
from app.repositories.user_repository import user_repository

@pytest.mark.asyncio
async def test_email_password_login_success(async_client):
    # Setup signed up user & activate
    signup_payload = {
        "full_name": "Active User",
        "email": "active@example.com",
        "mobile": "+919876543210",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    await async_client.post("/api/auth/signup", json=signup_payload)
    
    # Activate user directly in DB
    user = await user_repository.find_by_email("active@example.com")
    await user_repository.update_user(str(user.id), {"status": "active", "email_verified": True, "mobile_verified": True})

    # Test login
    login_payload = {
        "email": "ACTIVE@example.com",  # Test case normalization
        "password": "StrongPassword123!"
    }
    response = await async_client.post("/api/auth/login/email-password", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["user"]["email"] == "active@example.com"


@pytest.mark.asyncio
async def test_email_password_login_invalid_password(async_client):
    signup_payload = {
        "full_name": "Active User",
        "email": "active2@example.com",
        "mobile": "+919876543211",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    await async_client.post("/api/auth/signup", json=signup_payload)
    user = await user_repository.find_by_email("active2@example.com")
    await user_repository.update_user(str(user.id), {"status": "active"})

    login_payload = {
        "email": "active2@example.com",
        "password": "WrongPassword123!"
    }
    response = await async_client.post("/api/auth/login/email-password", json=login_payload)
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["error_code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_mobile_password_login_success(async_client):
    signup_payload = {
        "full_name": "Mobile User",
        "email": "mobile@example.com",
        "mobile": "+919876543212",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    await async_client.post("/api/auth/signup", json=signup_payload)
    user = await user_repository.find_by_mobile("+919876543212")
    await user_repository.update_user(str(user.id), {"status": "active"})

    login_payload = {
        "mobile": "+919876543212",
        "password": "StrongPassword123!"
    }
    response = await async_client.post("/api/auth/login/mobile-password", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["mobile"] == "+919876543212"


@pytest.mark.asyncio
async def test_login_pending_user(async_client):
    from app.repositories.user_repository import user_repository
    signup_payload = {
        "full_name": "Pending User",
        "email": "pending@example.com",
        "mobile": "+919876543213",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    await async_client.post("/api/auth/signup", json=signup_payload)
    user = await user_repository.find_by_email("pending@example.com")
    await user_repository.update_user(str(user.id), {"status": "suspended"})

    login_payload = {
        "email": "pending@example.com",
        "password": "StrongPassword123!"
    }
    response = await async_client.post("/api/auth/login/email-password", json=login_payload)
    assert response.status_code == 401
    assert response.json()["success"] is False
