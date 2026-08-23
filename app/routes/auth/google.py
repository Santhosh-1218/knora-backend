from typing import Optional
from fastapi import APIRouter, Query, Request, status
from fastapi.responses import RedirectResponse
import urllib.parse

from app.core.config import settings
from app.schemas.auth import TokenResponse
from app.schemas.response import APIResponse
from app.services.auth_service import auth_service
from app.services.google_oauth_service import google_oauth_service

router = APIRouter()


@router.get(
    "/google/login",
    summary="Get Google OAuth Authorization URL",
    description="Returns the Google OAuth 2.0 authorization URL for client redirection."
)
async def google_login(state: Optional[str] = Query(None)):
    if settings.GOOGLE_CLIENT_ID.startswith("mock_") or not settings.GOOGLE_CLIENT_ID:
        # In dev mode without real client ID, redirect to mock callback URL directly
        auth_url = f"{settings.GOOGLE_REDIRECT_URI}?code=mock_code_google_user_rahul"
    else:
        auth_url = google_oauth_service.get_authorization_url(state=state)

    return APIResponse(
        success=True,
        message="Google OAuth login URL generated",
        data={"auth_url": auth_url}
    )


@router.get(
    "/google/callback",
    summary="Google OAuth 2.0 Callback",
    description="Processes Google OAuth authorization code, verifies identity, links/creates user, and redirects with JWT tokens."
)
async def google_callback(
    code: str = Query(...),
    state: Optional[str] = Query(None),
    redirect: bool = Query(True, description="Whether to issue HTTP redirect to frontend URL"),
    request: Request = None
):
    user_agent = request.headers.get("user-agent") if request else None
    ip_address = request.client.host if request and request.client else None

    token_data = await auth_service.authenticate_google_callback(
        code=code,
        user_agent=user_agent,
        ip_address=ip_address
    )

    if redirect and settings.FRONTEND_URL:
        params = {
            "access_token": token_data.access_token,
            "refresh_token": token_data.refresh_token,
            "user_id": token_data.user.id,
            "email": token_data.user.email,
            "name": token_data.user.full_name
        }
        redirect_url = f"{settings.FRONTEND_URL}/auth/google/success?{urllib.parse.urlencode(params)}"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    return APIResponse(
        success=True,
        message="Google authentication successful",
        data=token_data
    )
