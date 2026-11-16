from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, Dict, List, Any

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int


class ErrorResponse(BaseModel):
    message: str
    errors: Optional[Dict[str, List[str]]] = None


class MessageResponse(BaseModel):
    message: str