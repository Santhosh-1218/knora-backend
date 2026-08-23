from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    email: Optional[str] = None
    email_verified: bool = False
    mobile: Optional[str] = None
    mobile_verified: bool = False
    google_linked: bool = False
    profile_image: Optional[str] = None
    status: str
    auth_methods: List[str] = Field(default_factory=list)
    created_at: datetime
    last_login_at: Optional[datetime] = None
