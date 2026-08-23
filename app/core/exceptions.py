from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class KnoraException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class AuthenticationError(KnoraException):
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class PermissionDeniedError(KnoraException):
    def __init__(self, message: str = "Permission denied", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class NotFoundError(KnoraException):
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class DuplicateEntityError(KnoraException):
    def __init__(self, message: str = "Resource already exists", error_code: str = "ALREADY_EXISTS", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class OTPError(KnoraException):
    def __init__(self, message: str, error_code: str = "OTP_INVALID", status_code: int = status.HTTP_400_BAD_REQUEST, details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details
        )


class RateLimitError(KnoraException):
    def __init__(self, message: str = "Too many requests. Please try again later.", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class ValidationException(KnoraException):
    def __init__(self, message: str = "Invalid input data", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )


async def knora_exception_handler(request: Request, exc: KnoraException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details
        }
    )


async def pydantic_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    simplified_errors = []
    for err in errors:
        loc = " -> ".join([str(item) for item in err.get("loc", []) if item != "body"])
        msg = err.get("msg", "Invalid field")
        simplified_errors.append({"field": loc, "message": msg})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Input validation failed",
            "error_code": "VALIDATION_ERROR",
            "details": simplified_errors
        }
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected internal server error occurred",
            "error_code": "INTERNAL_SERVER_ERROR",
            "details": None
        }
    )
