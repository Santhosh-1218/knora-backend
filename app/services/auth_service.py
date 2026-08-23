from typing import Any, Dict, Optional, Tuple
from app.core.exceptions import AuthenticationError, DuplicateEntityError, NotFoundError, OTPError
from app.core.security import hash_password, verify_password
from app.models.user import UserDocument
from app.repositories.user_repository import user_repository
from app.schemas.auth import SignupRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.google_oauth_service import google_oauth_service
from app.services.otp_service import otp_service
from app.services.token_service import token_service

# Dummy Argon2id hash for constant-time comparison on user-not-found
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$d3VtbXloYXNoZm9yY29uc3RhbnR0aW1l"


class AuthService:
    async def signup(
        self,
        req: SignupRequest,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        email_normalized = req.email.lower().strip()
        mobile = req.mobile.strip()

        # Check uniqueness
        email_exists, mobile_exists = await user_repository.exists_by_email_or_mobile(
            email_normalized, mobile
        )
        if email_exists:
            raise DuplicateEntityError("Email address is already registered", error_code="EMAIL_EXISTS")
        if mobile_exists:
            raise DuplicateEntityError("Mobile phone number is already registered", error_code="MOBILE_EXISTS")

        # Hash password
        pwd_hash = hash_password(req.password)

        user_dict = {
            "full_name": req.full_name.strip(),
            "email": email_normalized,
            "email_normalized": email_normalized,
            "email_verified": True,
            "mobile": mobile,
            "mobile_verified": False,
            "password_hash": pwd_hash,
            "status": "active",
            "auth_methods": ["password", "email_otp"]
        }

        user = await user_repository.create_user(user_dict)
        tokens = await token_service.issue_tokens(user, user_agent=user_agent, ip_address=ip_address)

        return {
            "user_id": str(user.id),
            "email": user.email,
            "mobile": user.mobile,
            "status": user.status,
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
            "expires_in": tokens.expires_in,
            "user": tokens.user.model_dump(),
            "message": "Account created successfully."
        }

    async def verify_email(
        self,
        email: str,
        otp: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        email_normalized = email.lower().strip()
        
        # 1. Verify OTP code in MongoDB
        await otp_service.verify_otp(email_normalized, "email", "verification", otp)

        # 2. Check if user document exists in MongoDB
        user = await user_repository.find_by_email(email_normalized)
        if not user:
            # Email verified prior to signup document creation (Pre-signup verification)
            return {
                "verified": True,
                "email": email_normalized,
                "user_status": "unregistered",
                "message": "Email verified successfully"
            }

        # If user document exists, activate user & return tokens
        updated_user = await user_repository.update_user(str(user.id), {
            "email_verified": True,
            "status": "active"
        })

        tokens = await token_service.issue_tokens(updated_user, user_agent=user_agent, ip_address=ip_address)

        return {
            "verified": True,
            "email": email_normalized,
            "user_status": "active",
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
            "expires_in": tokens.expires_in,
            "user": tokens.user.model_dump()
        }

    async def verify_mobile(self, mobile: str, otp: str) -> Dict[str, Any]:
        mobile_clean = mobile.strip()
        await otp_service.verify_otp(mobile_clean, "mobile", "verification", otp)

        user = await user_repository.find_by_mobile(mobile_clean)
        if not user:
            return {
                "verified": True,
                "mobile": mobile_clean,
                "user_status": "unregistered",
                "message": "Mobile number verified successfully"
            }

        updates: Dict[str, Any] = {"mobile_verified": True, "status": "active"}
        updated_user = await user_repository.update_user(str(user.id), updates)
        return {
            "verified": True,
            "mobile": mobile_clean,
            "user_status": updated_user.status if updated_user else "active"
        }

    async def login_email_password(
        self,
        email: str,
        password: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> TokenResponse:
        email_normalized = email.lower().strip()
        user = await user_repository.find_by_email(email_normalized)

        if not user or not user.password_hash:
            verify_password(password, DUMMY_HASH)
            raise AuthenticationError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        if user.status == "pending":
            user = await user_repository.update_user(str(user.id), {"status": "active", "email_verified": True})

        if user.status != "active":
            raise AuthenticationError(f"Account is currently {user.status}")

        return await token_service.issue_tokens(user, user_agent=user_agent, ip_address=ip_address)

    async def login_mobile_password(
        self,
        mobile: str,
        password: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> TokenResponse:
        mobile_clean = mobile.strip()
        user = await user_repository.find_by_mobile(mobile_clean)

        if not user or not user.password_hash:
            verify_password(password, DUMMY_HASH)
            raise AuthenticationError("Invalid mobile phone or password")

        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid mobile phone or password")

        if user.status == "pending":
            user = await user_repository.update_user(str(user.id), {"status": "active", "mobile_verified": True})

        if user.status != "active":
            raise AuthenticationError(f"Account is currently {user.status}")

        return await token_service.issue_tokens(user, user_agent=user_agent, ip_address=ip_address)

    async def send_login_otp(self, identifier: str, channel: str) -> Dict[str, Any]:
        clean_id = identifier.strip()
        if channel == "email":
            clean_id = clean_id.lower()
            user = await user_repository.find_by_email(clean_id)
        else:
            user = await user_repository.find_by_mobile(clean_id)

        if user:
            await otp_service.send_otp(clean_id, channel, "login")

        return {
            "message": f"If an account exists for {identifier}, a 6-digit OTP code has been sent."
        }

    async def verify_login_otp(
        self,
        identifier: str,
        channel: str,
        otp: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> TokenResponse:
        clean_id = identifier.strip()
        if channel == "email":
            clean_id = clean_id.lower()
            user = await user_repository.find_by_email(clean_id)
        else:
            user = await user_repository.find_by_mobile(clean_id)

        if not user:
            raise AuthenticationError("Authentication failed. User not found.")

        await otp_service.verify_otp(clean_id, channel, "login", otp)

        if user.status == "pending":
            user = await user_repository.update_user(str(user.id), {"status": "active"})

        await user_repository.add_auth_method(str(user.id), f"{channel}_otp")
        return await token_service.issue_tokens(user, user_agent=user_agent, ip_address=ip_address)

    async def authenticate_google_callback(
        self,
        code: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> TokenResponse:
        google_info = await google_oauth_service.verify_code_and_get_user_info(code)
        google_sub = google_info["sub"]
        google_email = google_info["email"]

        # Check existing user by Google sub
        user = await user_repository.find_by_google_sub(google_sub)

        if not user:
            # Check existing user by matching email
            user = await user_repository.find_by_email(google_email)
            if user:
                user = await user_repository.link_google_identity(
                    user_id=str(user.id),
                    google_sub=google_sub,
                    google_email=google_email,
                    name=google_info.get("name"),
                    picture=google_info.get("picture")
                )
            else:
                user_dict = {
                    "full_name": google_info.get("name") or google_email.split("@")[0],
                    "email": google_email,
                    "email_normalized": google_email,
                    "email_verified": True,
                    "google": {
                        "sub": google_sub,
                        "email": google_email,
                        "name": google_info.get("name"),
                        "picture": google_info.get("picture")
                    },
                    "profile_image": google_info.get("picture"),
                    "status": "active",
                    "auth_methods": ["google"]
                }
                user = await user_repository.create_user(user_dict)

        if user.status != "active":
            user = await user_repository.update_user(str(user.id), {"status": "active", "email_verified": True})

        return await token_service.issue_tokens(user, user_agent=user_agent, ip_address=ip_address)


auth_service = AuthService()
