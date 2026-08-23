from fastapi import APIRouter, Request, status
from app.schemas.auth import RefreshTokenRequest, TokenResponse
from app.schemas.response import APIResponse
from app.services.token_service import token_service

router = APIRouter()


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    summary="Rotate Refresh Token",
    description="Exchanges a valid refresh token for a new access token and rotated refresh token."
)
async def refresh_tokens(req: RefreshTokenRequest, request: Request):
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    token_data = await token_service.rotate_refresh_token(
        refresh_token=req.refresh_token,
        user_agent=user_agent,
        ip_address=ip_address
    )
    return APIResponse(
        success=True,
        message="Token successfully refreshed",
        data=token_data
    )


@router.post(
    "/logout",
    response_model=APIResponse[dict],
    summary="User Logout",
    description="Invalidates the provided refresh token session in MongoDB."
)
async def logout(req: RefreshTokenRequest):
    revoked = await token_service.revoke_session(req.refresh_token)
    return APIResponse(
        success=True,
        message="Successfully logged out",
        data={"session_revoked": revoked}
    )
