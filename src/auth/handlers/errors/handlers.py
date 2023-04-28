from typing import Optional, Type

from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from logrich.logger_ import log  # noqa
from pydantic import ValidationError
from starlette.datastructures import MutableHeaders
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


def get_app_middleware(app: FastAPI, middleware_class: Type) -> Optional[Middleware]:
    middleware_index = None
    for index, middleware in enumerate(app.user_middleware):
        if middleware.cls == middleware_class:
            middleware_index = index
    return None if middleware_index is None else app.user_middleware[middleware_index]


async def custom_headers(request: Request) -> MutableHeaders:
    request_origin = request.headers.get("origin", "")
    cors_middleware = get_app_middleware(app=request.app, middleware_class=CORSMiddleware)
    headers = MutableHeaders()
    if cors_middleware and "*" in cors_middleware.options["allow_origins"]:
        headers.append("Access-Control-Allow-Origin", "*")
        headers.append("Access-Control-Allow-Credentials", "true")
    elif cors_middleware and request_origin in cors_middleware.options["allow_origins"]:
        headers.append("Access-Control-Allow-Origin", request_origin)
        headers.append("Access-Control-Allow-Credentials", "true")
    return headers


def init_err_handlers(app: FastAPI) -> None:
    """Подключает общие обработчики исключений"""

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        headers = await custom_headers(request)
        return JSONResponse(status_code=400, content={"detail": exc.errors()}, headers=headers)  # type: ignore

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException) -> Response:
        headers = await custom_headers(request)
        exc.headers = headers  # type: ignore
        return await http_exception_handler(request, exc)
