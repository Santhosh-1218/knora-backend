import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.config import settings
from app.core.exceptions import OTPError, RateLimitError
from app.core.security import hash_otp, verify_otp_hash
from app.repositories.otp_repository import otp_repository
from app.services.email_service import email_service
from app.services.sms_service import sms_service


def _hash_identifier(identifier: str) -> str:
    return hashlib.sha256(identifier.lower().strip().encode("utf-8")).hexdigest()


def generate_6digit_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


class OTPService:
    async def send_otp(
        self,
        identifier: str,
        channel: str,  # "email" | "mobile"
        purpose: str   # "signup" | "login" | "verification"
    ) -> bool:
        identifier_clean = identifier.strip()
        if channel == "email":
            identifier_clean = identifier_clean.lower()

        id_hash = _hash_identifier(identifier_clean)

        # Check existing OTP resend cooldown
        existing = await otp_repository.find_latest_otp(id_hash, channel, purpose)
        if existing:
            now = datetime.now(timezone.utc)
            created_at = existing.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            
            elapsed = (now - created_at).total_seconds()
            if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
                wait_time = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
                raise RateLimitError(
                    message=f"Please wait {wait_time} seconds before requesting a new OTP."
                )

        # Generate new 6-digit OTP
        raw_otp = generate_6digit_otp()
        salt = secrets.token_hex(8)
        hashed_otp = hash_otp(raw_otp, salt)

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

        # Create record in DB
        await otp_repository.create_otp(
            identifier_hash=id_hash,
            channel=channel,
            purpose=purpose,
            otp_hash=hashed_otp,
            salt=salt,
            expires_at=expires_at,
            max_attempts=settings.OTP_MAX_ATTEMPTS
        )

        # Dispatch via provider asynchronously in background for fast response
        if channel == "email":
            asyncio.create_task(email_service.send_otp(identifier_clean, raw_otp, purpose))
            return True
        elif channel == "mobile":
            asyncio.create_task(sms_service.send_otp(identifier_clean, raw_otp, purpose))
            return True
        else:
            raise OTPError("Invalid verification channel", error_code="INVALID_CHANNEL")

    async def verify_otp(
        self,
        identifier: str,
        channel: str,
        purpose: str,
        submitted_otp: str
    ) -> bool:
        identifier_clean = identifier.strip()
        if channel == "email":
            identifier_clean = identifier_clean.lower()

        id_hash = _hash_identifier(identifier_clean)
        otp_record = await otp_repository.find_latest_otp(id_hash, channel, purpose)

        if not otp_record:
            raise OTPError("OTP has expired or does not exist", error_code="OTP_EXPIRED")

        # Check expiration
        now = datetime.now(timezone.utc)
        expires_at = otp_record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if now > expires_at:
            await otp_repository.delete_otp(otp_record.id)
            raise OTPError("OTP has expired. Please request a new code.", error_code="OTP_EXPIRED")

        # Check maximum verification attempts
        if otp_record.attempts >= otp_record.max_attempts:
            await otp_repository.delete_otp(otp_record.id)
            raise OTPError("Maximum OTP verification attempts exceeded. Please request a new OTP.", error_code="TOO_MANY_ATTEMPTS")

        # Verify hash
        is_valid = verify_otp_hash(submitted_otp, otp_record.otp_hash, otp_record.salt)

        if not is_valid:
            attempts = await otp_repository.increment_attempts(otp_record.id)
            remaining = otp_record.max_attempts - attempts
            if remaining <= 0:
                await otp_repository.delete_otp(otp_record.id)
                raise OTPError("Maximum OTP verification attempts exceeded. Please request a new OTP.", error_code="TOO_MANY_ATTEMPTS")
            raise OTPError(f"Invalid OTP code. {remaining} attempt(s) remaining.", error_code="OTP_INVALID")

        # Invalidate OTP on successful verification (single-use)
        await otp_repository.delete_otp(otp_record.id)
        return True


otp_service = OTPService()
