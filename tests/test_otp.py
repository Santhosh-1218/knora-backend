import pytest
import hashlib
from app.repositories.otp_repository import otp_repository
from app.repositories.user_repository import user_repository
from app.services.otp_service import _hash_identifier

@pytest.mark.asyncio
async def test_email_otp_send_and_verify(async_client):
    # Test sending OTP to a new email address
    send_res = await async_client.post("/api/auth/verification/email/send", json={"email": "fresh.otp@example.com"})
    assert send_res.status_code == 200
    assert send_res.json()["success"] is True

    # Retrieve created OTP record from repository
    id_hash = _hash_identifier("fresh.otp@example.com")
    otp_record = await otp_repository.find_latest_otp(id_hash, "email", "verification")
    assert otp_record is not None

    # Test wrong OTP verification
    verify_wrong = await async_client.post(
        "/api/auth/verification/email/verify",
        json={"email": "fresh.otp@example.com", "otp": "000000"}
    )
    assert verify_wrong.status_code == 400
    assert verify_wrong.json()["error_code"] == "OTP_INVALID"

    # Test resend cooldown rate limit (429)
    resend_cooldown = await async_client.post("/api/auth/verification/email/send", json={"email": "fresh.otp@example.com"})
    assert resend_cooldown.status_code == 429
    assert resend_cooldown.json()["error_code"] == "RATE_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_mobile_otp_send_and_verify(async_client):
    # Test sending OTP to a fresh mobile number
    send_res = await async_client.post("/api/auth/verification/mobile/send", json={"mobile": "+919876543999"})
    assert send_res.status_code == 200

    id_hash = _hash_identifier("+919876543999")
    otp_record = await otp_repository.find_latest_otp(id_hash, "mobile", "verification")
    assert otp_record is not None
