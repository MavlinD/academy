import hashlib
import hmac
import os
import time
from pathlib import Path
from typing import Any

from fastapi import HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from logrich.logger_ import log  # noqa
from starlette import status
from yarl import URL

from src.auth.assets import APIRouter
from src.auth.config import config, templates

router = APIRouter()


@router.get("/", include_in_schema=False, response_class=HTMLResponse)
async def read_home(request: Request) -> Any:
    """домашняя страница"""
    log.debug(request)
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login", include_in_schema=False, response_class=HTMLResponse)
async def login(request: Request) -> Any:
    """временный адрес для отладки"""

    return templates.TemplateResponse(
        "dev/login.html",
        {
            "request": request,
            "token_obtain_url": os.environ.get("LOGIN_CORS_URL_TEST", "/api/v2/auth/token-obtain"),
            "token_refresh_url": os.environ.get("REFRESH_CORS_URL_TEST", "/api/v2/auth/token-refresh"),
            "username": os.environ.get("USERNAME_CORS_URL_TEST"),
            "password": os.environ.get("PASSWORD_CORS_URL_TEST"),
        },
    )


@router.get("/sentry-debug", include_in_schema=False, response_class=HTMLResponse)
async def trigger_error() -> HTMLResponse:
    """точка для тестирования доступности sentry"""
    # result = 1 / 0
    result = 1 + "1"  # type: ignore
    return HTMLResponse(content=result)


@router.get("/pub-key", response_class=PlainTextResponse, tags=["Service"])
async def read_pub_key() -> str:
    """точка для предоставления публичного ключа"""
    return config.PUBLIC_KEY


@router.get("/{article:str}", include_in_schema=False, response_class=HTMLResponse)
async def read_wiki_structure(request: Request) -> Any:
    """страницы помощи"""
    url = URL(str(request.url))
    article = url.name or url.parts[-2]
    try:
        return templates.TemplateResponse(f"{article}/index.html", {"request": request})
    except Exception:
        raise HTTPException(status_code=404, detail="Ничего нет")


@router.get("/search/search_index.json", include_in_schema=False, response_class=HTMLResponse)
async def search(request: Request) -> Any:
    """поиск"""
    return templates.TemplateResponse("search/search_index.json", {"request": request})


def process_(max_range: int) -> None | str:
    signature = None
    for i in range(0, max_range):
        signature = doHeavyStuff(f"item{i}.")
    return signature


def doHeavyStuff(message: str) -> str:
    api_secret = "secret"
    list_length = 10000
    message_ = message * list_length
    # base64.b64encode(hmac_result.digest()
    return hmac.new(
        bytes(api_secret, "utf-8"),
        msg=bytes(message_[:-1], "utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


@router.get(
    "/test/stress",
    include_in_schema=False,
    response_class=JSONResponse,
    status_code=status.HTTP_200_OK,
    tags=["Service"],
)
def stress_test(
    iterate: int = Query(default=1, ge=1, description="кол-во итераций хеширования в нагрузочном тесте"),
) -> JSONResponse:
    """stress test view"""
    tic = time.perf_counter()
    signature = process_(int(iterate))
    # log.debug(signature)
    toc = time.perf_counter()
    elapsed_time = toc - tic
    format_time = f"{elapsed_time:0.3f} seconds"
    content = {
        "message": "Test complete",
        "signature": signature,
        "elapseDuration": format_time,
    }
    return JSONResponse(status_code=200, content=content)
