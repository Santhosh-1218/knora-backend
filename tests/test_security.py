import pytest

@pytest.mark.asyncio
async def test_unauthorized_me_access(async_client):
    res = await async_client.get("/api/auth/me")
    assert res.status_code == 401
    data = res.json()
    assert data["success"] is False
    assert data["error_code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_enumeration_protection_email_login(async_client):
    # Non-existent email login should fail with generic authentication error
    login_payload = {
        "email": "nonexistent.user.12345@example.com",
        "password": "SomePassword123!"
    }
    res = await async_client.post("/api/auth/login/email-password", json=login_payload)
    assert res.status_code == 401
    data = res.json()
    assert data["message"] == "Invalid email or password"
    assert data["error_code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_enumeration_protection_mobile_login(async_client):
    login_payload = {
        "mobile": "+919999999999",
        "password": "SomePassword123!"
    }
    res = await async_client.post("/api/auth/login/mobile-password", json=login_payload)
    assert res.status_code == 401
    data = res.json()
    assert data["message"] == "Invalid mobile phone or password"
    assert data["error_code"] == "AUTHENTICATION_FAILED"
