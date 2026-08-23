from typing import Optional, List
from pydantic import BaseModel, Field


class CarouselSlideCreate(BaseModel):
    title: str = Field(..., example="1,000+ Academic Videos & Notes")
    subtitle: str = Field(..., example="Structured learning content for university students.")
    badge: str = Field(..., example="ACADEMICS")
    cta_text: str = Field(..., alias="ctaText", example="Explore Academics")
    target_path: str = Field(..., alias="targetPath", example="/academics")
    is_public: bool = Field(default=True, alias="isPublic")
    feature_name: Optional[str] = Field(default=None, alias="featureName")
    icon_name: str = Field(default="BookOpen", alias="iconName")
    accent_color: str = Field(default="#1A73E8", alias="accentColor")
    bg_image: str = Field(..., alias="bgImage")
    order: int = Field(default=0)
    is_active: bool = Field(default=True, alias="isActive")

    class Config:
        populate_by_name = True


class CarouselSlideUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    badge: Optional[str] = None
    cta_text: Optional[str] = Field(default=None, alias="ctaText")
    target_path: Optional[str] = Field(default=None, alias="targetPath")
    is_public: Optional[bool] = Field(default=None, alias="isPublic")
    feature_name: Optional[str] = Field(default=None, alias="featureName")
    icon_name: Optional[str] = Field(default=None, alias="iconName")
    accent_color: Optional[str] = Field(default=None, alias="accentColor")
    bg_image: Optional[str] = Field(default=None, alias="bgImage")
    order: Optional[int] = None
    is_active: Optional[bool] = Field(default=None, alias="isActive")

    class Config:
        populate_by_name = True


class CarouselSlideResponse(BaseModel):
    id: str
    title: str
    subtitle: str
    badge: str
    ctaText: str
    targetPath: str
    isPublic: bool
    featureName: Optional[str] = None
    iconName: str
    accentColor: str
    bgImage: str
    order: int
    isActive: bool

    class Config:
        populate_by_name = True
