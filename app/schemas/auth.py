import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from app.core.exceptions import ValidationException
from app.schemas.otp import normalize_and_validate_mobile
from app.schemas.user import UserResponse


class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    mobile: str
    password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str = Field(..., min_length=6, max_length=128)

    @field_validator("full_name", mode="after")
    def validate_name(cls, v: str) -> str:
        name = v.strip()
        if not name:
            raise ValidationException("Full name cannot be empty or blank")
        return name

    @field_validator("email", mode="after")
    def normalize_email(cls, v: str) -> str:
        return str(v).strip().lower()

    @field_validator("mobile", mode="after")
    def validate_mobile(cls, v: str) -> str:
        return normalize_and_validate_mobile(v)

    @field_validator("password", mode="after")
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValidationException("Password must be at least 6 characters long")
        return v

    @model_validator(mode="after")
    def validate_password_confirmation(self) -> "SignupRequest":
        if self.password != self.confirm_password:
            raise ValidationException("Password and confirm_password do not match")
        return self


class EmailPasswordLoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", mode="after")
    def normalize_email(cls, v: str) -> str:
        return str(v).strip().lower()


class MobilePasswordLoginRequest(BaseModel):
    mobile: str
    password: str

    @field_validator("mobile", mode="after")
    def validate_mobile(cls, v: str) -> str:
        return normalize_and_validate_mobile(v)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

