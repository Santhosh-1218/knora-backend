import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, create_refresh_token, decode_jwt_token, hash_token
from app.models.user import UserDocument
from app.repositories.session_repository import session_repository
from app.repositories.user_repository import user_repository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserResponse


class TokenService:
    async def issue_tokens(
        self,
        user: UserDocument,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> TokenResponse:
        user_id = str(user.id)
        
        # Create access token
        access_token = create_access_token(
            subject=user_id,
            extra_claims={
                "email": user.email_normalized,
                "mobile": user.mobile,
                "full_name": user.full_name
            }
        )

        # Create refresh token & session record
        refresh_token, jti = create_refresh_token(subject=user_id)
        refresh_hash = hash_token(refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        await session_repository.create_session(
            user_id=user_id,
            refresh_token_hash=refresh_hash,
            jti=jti,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )

        # Update last login timestamp asynchronously
        await user_repository.update_last_login(user_id)

        user_response = UserResponse(
            id=user_id,
            full_name=user.full_name,
            email=user.email,
            email_verified=user.email_verified,
            mobile=user.mobile,
            mobile_verified=user.mobile_verified,
            google_linked=user.google is not None,
            profile_image=user.profile_image,
            status=user.status,
            auth_methods=user.auth_methods,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )

    async def rotate_refresh_token(
        self,
        refresh_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> TokenResponse:
        # Decode JWT signature
        payload = decode_jwt_token(refresh_token)
        if payload.get("type") != "refresh":
            raise AuthenticationError("Provided token is not a refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")

        refresh_hash = hash_token(refresh_token)
        session = await session_repository.find_session_by_hash(refresh_hash)
        if not session:
            # Refresh token already used or revoked - potential token reuse attack
            raise AuthenticationError("Invalid or expired refresh session")

        # Delete old session (Rotation)
        await session_repository.delete_session_by_hash(refresh_hash)

        # Fetch user & check status
        user = await user_repository.find_by_id(user_id)
        if not user:
            raise AuthenticationError("User associated with token no longer exists")

        if user.status != "active":
            raise AuthenticationError(f"Account is currently {user.status}")

        # Issue new token pair
        return await self.issue_tokens(user, user_agent=user_agent, ip_address=ip_address)

    async def revoke_session(self, refresh_token: str) -> bool:
        try:
            refresh_hash = hash_token(refresh_token)
            return await session_repository.delete_session_by_hash(refresh_hash)
        except Exception:
            return False


token_service = TokenService()
