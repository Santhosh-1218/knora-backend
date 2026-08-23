import re
import phonenumbers
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.core.exceptions import ValidationException


def normalize_and_validate_mobile(v: str) -> str:
    if not v or not v.strip():
        raise ValidationException("Mobile number is required")
    v = v.strip()
    try:
        # Default region set to IN if no leading plus is given, or parse international format
        parsed = phonenumbers.parse(v, "IN")
        if not phonenumbers.is_valid_number(parsed):
            raise ValidationException("Invalid mobile phone number")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        # Fallback regex for E.164 if phonenumbers fails
        if re.match(r"^\+[1-9]\d{1,14}$", v):
            return v
        raise ValidationException("Invalid mobile phone number format. Must be in E.164 format (e.g., +919876543210).")


class SendEmailOTPRequest(BaseModel):
    email: EmailStr

    @field_validator("email", mode="after")
    def normalize_email(cls, v: str) -> str:
        return str(v).strip().lower()


class VerifyEmailOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

    @field_validator("email", mode="after")
    def normalize_email(cls, v: str) -> str:
        return str(v).strip().lower()

    @field_validator("otp", mode="after")
    def validate_otp_format(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit() or len(v) != 6:
            raise ValidationException("OTP must be exactly 6 digits")
        return v


class SendMobileOTPRequest(BaseModel):
    mobile: str

    @field_validator("mobile", mode="after")
    def validate_mobile(cls, v: str) -> str:
        return normalize_and_validate_mobile(v)


class VerifyMobileOTPRequest(BaseModel):
    mobile: str
    otp: str = Field(..., min_length=6, max_length=6)

    @field_validator("mobile", mode="after")
    def validate_mobile(cls, v: str) -> str:
        return normalize_and_validate_mobile(v)

    @field_validator("otp", mode="after")
    def validate_otp_format(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit() or len(v) != 6:
            raise ValidationException("OTP must be exactly 6 digits")
        return v
