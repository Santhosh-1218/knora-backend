import time
import pytest
from app.repositories.user_repository import user_repository


@pytest.mark.asyncio
async def test_auth_performance_benchmarks(async_client):
    # 1. Setup user
    signup_payload = {
        "full_name": "Perf User",
        "email": "perf@example.com",
        "mobile": "+919876543218",
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!"
    }
    await async_client.post("/api/auth/signup", json=signup_payload)
    user = await user_repository.find_by_email("perf@example.com")
    await user_repository.update_user(str(user.id), {"status": "active"})

    # 2. Benchmark Email/Password Login
    t0 = time.perf_counter()
    login_res = await async_client.post(
        "/api/auth/login/email-password",
        json={"email": "perf@example.com", "password": "StrongPassword123!"}
    )
    t1 = time.perf_counter()
    login_latency_ms = (t1 - t0) * 1000
    assert login_res.status_code == 200

    tokens = login_res.json()["data"]
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # 3. Benchmark /me Endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    t0 = time.perf_counter()
    me_res = await async_client.get("/api/auth/me", headers=headers)
    t1 = time.perf_counter()
    me_latency_ms = (t1 - t0) * 1000
    assert me_res.status_code == 200

    # 4. Benchmark Token Refresh
    t0 = time.perf_counter()
    refresh_res = await async_client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    t1 = time.perf_counter()
    refresh_latency_ms = (t1 - t0) * 1000
    assert refresh_res.status_code == 200

    # 5. Benchmark Google Callback Mock
    t0 = time.perf_counter()
    google_res = await async_client.get("/api/auth/google/callback?code=mock_code_perf_123&redirect=false")
    t1 = time.perf_counter()
    google_latency_ms = (t1 - t0) * 1000
    assert google_res.status_code == 200

    print(f"\n--- BENCHMARK RESULTS ---")
    print(f"Email/Password Login Latency: {login_latency_ms:.2f} ms")
    print(f"GET /me Latency:              {me_latency_ms:.2f} ms")
    print(f"Token Refresh Latency:        {refresh_latency_ms:.2f} ms")
    print(f"Google Callback Latency:       {google_latency_ms:.2f} ms")
