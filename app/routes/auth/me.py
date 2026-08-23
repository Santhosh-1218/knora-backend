from fastapi import APIRouter, Depends
from app.routes.deps import get_current_user_response
from app.schemas.response import APIResponse
from app.schemas.user import UserResponse

router = APIRouter()


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Get Current User Profile",
    description="Returns the authenticated user's safe profile information (requires valid Bearer access token)."
)
async def get_me(current_user: UserResponse = Depends(get_current_user_response)):
    return APIResponse(
        success=True,
        message="Current user profile retrieved",
        data=current_user
    )
