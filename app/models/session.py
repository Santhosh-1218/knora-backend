from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SessionDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    refresh_token_hash: str
    jti: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True)
