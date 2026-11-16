from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=5)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 5:
            raise ValueError("Password must be at least 5 characters")
        # Check for lowercase, uppercase, special char
        has_lower = any(c.islower() for c in v)
        has_upper = any(c.isupper() for c in v)
        has_special = any(c in "#_-$" for c in v)
        if not (has_lower and has_upper and has_special):
            raise ValueError("Password must contain lowercase, uppercase, and special character (# _ - $)")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: str

    class Config:
        from_attributes = True