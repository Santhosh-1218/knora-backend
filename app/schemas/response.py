from typing import Generic, Optional, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None
    error_code: Optional[str] = None
    details: Optional[Any] = None
