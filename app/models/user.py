from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class GoogleIdentity(BaseModel):
    sub: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None


class UserDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    full_name: str
    email: Optional[str] = None
    email_normalized: Optional[str] = None
    email_verified: bool = False
    
    mobile: Optional[str] = None
    mobile_verified: bool = False

    password_hash: Optional[str] = None
    google: Optional[GoogleIdentity] = None
    profile_image: Optional[str] = None
    status: str = "active"  # "pending", "active", "suspended", "disabled"

    auth_methods: List[str] = Field(default_factory=list)  # ["password", "google", "otp"]

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(populate_by_name=True)
