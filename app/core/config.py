import json
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "development"
    DEBUG: bool = True

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/"
    MONGODB_DATABASE: str = "knora"

    # JWT
    JWT_SECRET: str = "knora_dev_secret_key_must_be_long_enough_for_security_12345"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # Frontend & CORS
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Messaging Providers
    EMAIL_PROVIDER: str = "smtp"
    EMAIL_FROM: str = "KNORA Verification <boppudisanthosh404@gmail.com>"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "boppudisanthosh404@gmail.com"
    SMTP_PASSWORD: str = "ojvnfazhrvqsuejw"
    SMS_PROVIDER: str = "dev"
    SMS_FROM: str = "KNORA"

    # OTP Controls
    OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60
    ENABLE_DEV_OTP_LOGGING: bool = True

    # Cloudflare R2 Storage
    CLOUDFLARE_R2_ACCOUNT_ID: str = ""
    CLOUDFLARE_R2_ACCESS_KEY_ID: str = ""
    CLOUDFLARE_R2_SECRET_ACCESS_KEY: str = ""
    CLOUDFLARE_R2_API_TOKEN: str = ""
    CLOUDFLARE_R2_ENDPOINT_URL: str = ""
    CLOUDFLARE_R2_BUCKET_NAME: str = "wwi-resumes"
    CLOUDFLARE_R2_PUBLIC_DOMAIN: str = ""


settings = Settings()
# Force uvicorn reloader to pick up real Google OAuth keys from .env


