from abc import ABC, abstractmethod
from app.core.config import settings
from app.core.logging import logger


class SmsProvider(ABC):
    @abstractmethod
    async def send_otp(self, to_mobile: str, otp: str, purpose: str) -> bool:
        pass


class DevSmsProvider(SmsProvider):
    async def send_otp(self, to_mobile: str, otp: str, purpose: str) -> bool:
        if settings.ENABLE_DEV_OTP_LOGGING:
            logger.info(f"[DEV SMS OTP] Sent to: {to_mobile} | Purpose: {purpose} | OTP: {otp}")
        else:
            logger.info(f"[DEV SMS OTP] Sent to: {to_mobile} | Purpose: {purpose}")
        return True


def get_sms_provider() -> SmsProvider:
    provider_name = settings.SMS_PROVIDER.lower()
    if provider_name == "dev":
        return DevSmsProvider()
    # Easily extensible for Twilio, MSG91, AWS SNS, etc.
    return DevSmsProvider()


sms_service = get_sms_provider()
