import pytest
from app.repositories.user_repository import user_repository

@pytest.mark.asyncio
async def test_access_token_and_me_endpoint(async_client):
    signup_payload = {
        "full_name": "Token Tester",
        "email": "token@example.com",
        "mobile": "+919876543216",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    await async_client.post("/api/auth/signup", json=signup_payload)
    user = await user_repository.find_by_email("token@example.com")
    await user_repository.update_user(str(user.id), {"status": "active"})

    login_res = await async_client.post(
        "/api/auth/login/email-password",
        json={"email": "token@example.com", "password": "StrongPassword123!"}
    )
    tokens = login_res.json()["data"]
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Test /me with Bearer token
    headers = {"Authorization": f"Bearer {access_token}"}
    me_res = await async_client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["success"] is True
    assert me_data["data"]["email"] == "token@example.com"


@pytest.mark.asyncio
async def test_refresh_token_rotation_and_logout(async_client):
    signup_payload = {
        "full_name": "Refresh Tester",
        "email": "refresh@example.com",
        "mobile": "+919876543217",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    await async_client.post("/api/auth/signup", json=signup_payload)
    user = await user_repository.find_by_email("refresh@example.com")
    await user_repository.update_user(str(user.id), {"status": "active"})

    login_res = await async_client.post(
        "/api/auth/login/email-password",
        json={"email": "refresh@example.com", "password": "StrongPassword123!"}
    )
    tokens = login_res.json()["data"]
    old_refresh_token = tokens["refresh_token"]

    # Rotate refresh token
    refresh_res = await async_client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh_token}
    )
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()["data"]
    new_refresh_token = new_tokens["refresh_token"]
    assert new_refresh_token != old_refresh_token

    # Attempting to use OLD refresh token should be rejected (Rotation security!)
    reuse_res = await async_client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh_token}
    )
    assert reuse_res.status_code == 401

    # Test logout with new refresh token
    logout_res = await async_client.post(
        "/api/auth/logout",
        json={"refresh_token": new_refresh_token}
    )
    assert logout_res.status_code == 200

    # Refresh after logout should fail
    after_logout_res = await async_client.post(
        "/api/auth/refresh",
        json={"refresh_token": new_refresh_token}
    )
    assert after_logout_res.status_code == 401
