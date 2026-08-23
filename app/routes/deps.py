from typing import Optional
from fastapi import Depends, Header, Request
from app.core.exceptions import AuthenticationError
from app.core.security import decode_jwt_token
from app.models.user import UserDocument
from app.repositories.user_repository import user_repository
from app.schemas.user import UserResponse


async def get_current_user(authorization: Optional[str] = Header(None)) -> UserDocument:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("Missing or invalid Authorization header. Token required.")

    token = authorization.split(" ")[1]
    payload = decode_jwt_token(token)

    if payload.get("type") != "access":
        raise AuthenticationError("Provided token is not an access token.")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token claims.")

    user = await user_repository.find_by_id(user_id)
    if not user:
        raise AuthenticationError("User not found.")

    if user.status != "active":
        raise AuthenticationError(f"Account is currently {user.status}.")

    return user


async def get_current_user_response(current_user: UserDocument = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        full_name=current_user.full_name,
        email=current_user.email,
        email_verified=current_user.email_verified,
        mobile=current_user.mobile,
        mobile_verified=current_user.mobile_verified,
        google_linked=current_user.google is not None,
        profile_image=current_user.profile_image,
        status=current_user.status,
        auth_methods=current_user.auth_methods,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )
