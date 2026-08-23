from fastapi import APIRouter, Request, status
from app.schemas.auth import TokenResponse
from app.schemas.otp import (
    SendEmailOTPRequest,
    SendMobileOTPRequest,
    VerifyEmailOTPRequest,
    VerifyMobileOTPRequest,
)
from app.schemas.response import APIResponse
from app.services.auth_service import auth_service
from app.services.otp_service import otp_service

router = APIRouter()

# --- Email Verification ---

@router.post(
    "/verification/email/send",
    response_model=APIResponse[dict],
    summary="Send Email Verification OTP",
    description="Sends a 6-digit verification OTP to the user's email address."
)
async def send_email_verification_otp(req: SendEmailOTPRequest):
    await otp_service.send_otp(req.email, "email", "verification")
    return APIResponse(
        success=True,
        message=f"Verification OTP successfully sent to {req.email}"
    )


@router.post(
    "/verification/email/verify",
    response_model=APIResponse[dict],
    summary="Verify Email OTP",
    description="Verifies the 6-digit email OTP and updates email verification status."
)
async def verify_email_otp(req: VerifyEmailOTPRequest):
    result = await auth_service.verify_email(req.email, req.otp)
    return APIResponse(
        success=True,
        message="Email verified successfully",
        data=result
    )

# --- Mobile Verification ---

@router.post(
    "/verification/mobile/send",
    response_model=APIResponse[dict],
    summary="Send Mobile Verification OTP",
    description="Sends a 6-digit SMS verification OTP to the user's mobile number."
)
async def send_mobile_verification_otp(req: SendMobileOTPRequest):
    await otp_service.send_otp(req.mobile, "mobile", "verification")
    return APIResponse(
        success=True,
        message=f"Verification OTP successfully sent to {req.mobile}"
    )


@router.post(
    "/verification/mobile/verify",
    response_model=APIResponse[dict],
    summary="Verify Mobile OTP",
    description="Verifies the 6-digit SMS OTP and updates mobile verification status."
)
async def verify_mobile_otp(req: VerifyMobileOTPRequest):
    result = await auth_service.verify_mobile(req.mobile, req.otp)
    return APIResponse(
        success=True,
        message="Mobile number verified successfully",
        data=result
    )

# --- Email OTP Login ---

@router.post(
    "/login/email-otp/send",
    response_model=APIResponse[dict],
    summary="Send Email Login OTP",
    description="Sends a 6-digit login OTP to an existing user's email."
)
async def send_email_login_otp(req: SendEmailOTPRequest):
    result = await auth_service.send_login_otp(req.email, "email")
    return APIResponse(
        success=True,
        message=result["message"]
    )


@router.post(
    "/login/email-otp/verify",
    response_model=APIResponse[TokenResponse],
    summary="Verify Email Login OTP",
    description="Verifies the 6-digit email login OTP and issues authentication tokens."
)
async def verify_email_login_otp(req: VerifyEmailOTPRequest, request: Request):
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    token_data = await auth_service.verify_login_otp(
        identifier=req.email,
        channel="email",
        otp=req.otp,
        user_agent=user_agent,
        ip_address=ip_address
    )
    return APIResponse(
        success=True,
        message="Email OTP login successful",
        data=token_data
    )

# --- Mobile OTP Login ---

@router.post(
    "/login/mobile-otp/send",
    response_model=APIResponse[dict],
    summary="Send Mobile Login OTP",
    description="Sends a 6-digit login SMS OTP to an existing user's mobile number."
)
async def send_mobile_login_otp(req: SendMobileOTPRequest):
    result = await auth_service.send_login_otp(req.mobile, "mobile")
    return APIResponse(
        success=True,
        message=result["message"]
    )


@router.post(
    "/login/mobile-otp/verify",
    response_model=APIResponse[TokenResponse],
    summary="Verify Mobile Login OTP",
    description="Verifies the 6-digit mobile login SMS OTP and issues authentication tokens."
)
async def verify_mobile_login_otp(req: VerifyMobileOTPRequest, request: Request):
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    token_data = await auth_service.verify_login_otp(
        identifier=req.mobile,
        channel="mobile",
        otp=req.otp,
        user_agent=user_agent,
        ip_address=ip_address
    )
    return APIResponse(
        success=True,
        message="Mobile OTP login successful",
        data=token_data
    )
