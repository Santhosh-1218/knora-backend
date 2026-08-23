from fastapi import APIRouter, Request, status
from app.schemas.auth import EmailPasswordLoginRequest, MobilePasswordLoginRequest, TokenResponse
from app.schemas.response import APIResponse
from app.services.auth_service import auth_service

router = APIRouter()


@router.post(
    "/login/email-password",
    response_model=APIResponse[TokenResponse],
    summary="Login with Email + Password",
    description="Authenticates an active user using email and Argon2id password."
)
async def login_email_password(req: EmailPasswordLoginRequest, request: Request):
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    token_data = await auth_service.login_email_password(
        email=req.email,
        password=req.password,
        user_agent=user_agent,
        ip_address=ip_address
    )
    return APIResponse(
        success=True,
        message="Email/Password login successful",
        data=token_data
    )


@router.post(
    "/login/mobile-password",
    response_model=APIResponse[TokenResponse],
    summary="Login with Mobile + Password",
    description="Authenticates an active user using normalized E.164 mobile number and Argon2id password."
)
async def login_mobile_password(req: MobilePasswordLoginRequest, request: Request):
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    token_data = await auth_service.login_mobile_password(
        mobile=req.mobile,
        password=req.password,
        user_agent=user_agent,
        ip_address=ip_address
    )
    return APIResponse(
        success=True,
        message="Mobile/Password login successful",
        data=token_data
    )
