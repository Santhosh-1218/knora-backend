from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class OTPDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    identifier_hash: str
    channel: str  # "email", "mobile"
    purpose: str  # "signup", "login", "verification"
    otp_hash: str
    salt: str
    attempts: int = 0
    max_attempts: int = 5
    resend_count: int = 0
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True)
