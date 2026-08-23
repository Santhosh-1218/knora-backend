from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CarouselSlideModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    subtitle: str
    badge: str
    cta_text: str = Field(alias="ctaText")
    target_path: str = Field(alias="targetPath")
    is_public: bool = Field(default=True, alias="isPublic")
    feature_name: Optional[str] = Field(default=None, alias="featureName")
    icon_name: str = Field(default="BookOpen", alias="iconName")
    accent_color: str = Field(default="#1A73E8", alias="accentColor")
    bg_image: str = Field(alias="bgImage")
    order: int = 0
    is_active: bool = Field(default=True, alias="isActive")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
