from fastapi import APIRouter, status, Query
from app.schemas.auth import SignupRequest
from app.schemas.response import APIResponse
from app.services.auth_service import auth_service
from app.repositories.user_repository import user_repository

router = APIRouter()


@router.get(
    "/check-email",
    response_model=APIResponse[dict],
    summary="Check Email Availability",
    description="Checks whether an email address is already registered in KNORA."
)
async def check_email(email: str = Query(..., description="Email address to check")):
    email_clean = email.lower().strip()
    user = await user_repository.find_by_email(email_clean)
    exists = user is not None
    return APIResponse(
        success=True,
        message="Email status checked",
        data={
            "email": email_clean,
            "exists": exists,
            "available": not exists
        }
    )


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[dict],
    summary="User Signup",
    description="Registers a new Knora user with email, mobile, and password. Dispatches real verification OTP."
)
async def signup(req: SignupRequest):
    result = await auth_service.signup(req)
    return APIResponse(
        success=True,
        message="Registration initiated. A 6-digit OTP code has been sent to your email.",
        data=result
    )
