import pytest

@pytest.mark.asyncio
async def test_valid_signup(async_client):
    payload = {
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "mobile": "+919876543210",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    response = await async_client.post("/api/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "john.doe@example.com"
    assert data["data"]["mobile"] == "+919876543210"
    assert data["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_signup_duplicate_email(async_client):
    payload = {
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "mobile": "+919876543210",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    res1 = await async_client.post("/api/auth/signup", json=payload)
    assert res1.status_code == 201

    payload2 = {
        "full_name": "Jane Doe",
        "email": "john.doe@example.com",  # Duplicate email
        "mobile": "+919876543211",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    res2 = await async_client.post("/api/auth/signup", json=payload2)
    assert res2.status_code == 409
    data = res2.json()
    assert data["success"] is False
    assert data["error_code"] == "EMAIL_EXISTS"


@pytest.mark.asyncio
async def test_signup_duplicate_mobile(async_client):
    payload = {
        "full_name": "John Doe",
        "email": "john1@example.com",
        "mobile": "+919876543210",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    res1 = await async_client.post("/api/auth/signup", json=payload)
    assert res1.status_code == 201

    payload2 = {
        "full_name": "Jane Doe",
        "email": "jane2@example.com",
        "mobile": "+919876543210",  # Duplicate mobile
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    res2 = await async_client.post("/api/auth/signup", json=payload2)
    assert res2.status_code == 409
    data = res2.json()
    assert data["success"] is False
    assert data["error_code"] == "MOBILE_EXISTS"


@pytest.mark.asyncio
async def test_signup_invalid_email(async_client):
    payload = {
        "full_name": "John Doe",
        "email": "not-an-email",
        "mobile": "+919876543210",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    res = await async_client.post("/api/auth/signup", json=payload)
    assert res.status_code == 422
    assert res.json()["success"] is False


@pytest.mark.asyncio
async def test_signup_weak_password(async_client):
    payload = {
        "full_name": "John Doe",
        "email": "john.weak@example.com",
        "mobile": "+919876543210",
        "password": "weak",
        "confirm_password": "weak"
    }
    res = await async_client.post("/api/auth/signup", json=payload)
    assert res.status_code == 422
    assert res.json()["success"] is False


@pytest.mark.asyncio
async def test_signup_password_mismatch(async_client):
    payload = {
        "full_name": "John Doe",
        "email": "john.mismatch@example.com",
        "mobile": "+919876543210",
        "password": "StrongPassword123!",
        "confirm_password": "DifferentPassword123!"
    }
    res = await async_client.post("/api/auth/signup", json=payload)
    assert res.status_code == 422
    assert res.json()["success"] is False
