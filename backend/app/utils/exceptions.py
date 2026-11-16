from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
from app.schemas.common import ErrorResponse


class UnauthenticatedException(Exception):
    def __init__(self, detail: str = "Unauthenticated"):
        self.detail = detail


class ForbiddenException(Exception):
    def __init__(self, detail: str = "Forbidden for you"):
        self.detail = detail


async def unauthenticated_exception_handler(request: Request, exc: UnauthenticatedException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": exc.detail},
    )


async def forbidden_exception_handler(request: Request, exc: ForbiddenException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"message": exc.detail},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        if field not in errors:
            errors[field] = []
        errors[field].append(error["msg"])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Invalid fields",
            "errors": errors,
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 401:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Unauthenticated"},
        )
    elif exc.status_code == 403:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Forbidden for you"},
        )
    elif exc.status_code == 422:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": "Invalid fields", "errors": {}},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )