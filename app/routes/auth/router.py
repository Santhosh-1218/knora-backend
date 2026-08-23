from fastapi import APIRouter
from app.routes.auth.signup import router as signup_router
from app.routes.auth.login import router as login_router
from app.routes.auth.otp import router as otp_router
from app.routes.auth.google import router as google_router
from app.routes.auth.token import router as token_router
from app.routes.auth.me import router as me_router

auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

auth_router.include_router(signup_router)
auth_router.include_router(login_router)
auth_router.include_router(otp_router)
auth_router.include_router(google_router)
auth_router.include_router(token_router)
auth_router.include_router(me_router)
