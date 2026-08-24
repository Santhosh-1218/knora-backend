from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import (
    KnoraException,
    global_exception_handler,
    knora_exception_handler,
    pydantic_validation_exception_handler,
)
from app.core.logging import logger, setup_logging
from app.db.indexes import create_mongo_indexes
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from app.routes.auth.router import auth_router
from app.routes.carousel import carousel_router, admin_carousel_router
from app.routes.resume import resume_router
from app.schemas.response import APIResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Initializing Knora Authentication Service...")
    await connect_to_mongo()
    try:
        await create_mongo_indexes()
    except Exception as e:
        logger.warning(f"Could not automatically create MongoDB indexes on startup: {e}")
    
    yield
    
    logger.info("Shutting down Knora Authentication Service...")
    await close_mongo_connection()


app = FastAPI(
    title="Knora Authentication Backend API",
    description="High-performance, modular authentication microservice for Knora platform supporting Email/Mobile Password, Email/Mobile OTP, and Google OAuth 2.0.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(KnoraException, knora_exception_handler)
app.add_exception_handler(RequestValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Routers
app.include_router(auth_router)
app.include_router(carousel_router)
app.include_router(admin_carousel_router)
app.include_router(resume_router)


@app.get("/", tags=["Health Check"])
async def root():
    return APIResponse(
        success=True,
        message="Knora Authentication API Service is operational",
        data={"version": "1.0.0", "environment": settings.APP_ENV}
    )


@app.get("/health", tags=["Health Check"])
async def health_check():
    return APIResponse(
        success=True,
        message="Healthy",
        data={"status": "UP", "database": settings.MONGODB_DATABASE}
    )
