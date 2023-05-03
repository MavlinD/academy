from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse
from logrich.logger_ import log  # noqa

from src.auth.assets import APIRouter
from src.auth.config import templates

router = APIRouter()


@router.get("/", include_in_schema=False, response_class=HTMLResponse)
async def read_home(request: Request) -> Any:
    """домашняя страница"""
    return templates.TemplateResponse("index.html", {"request": request})
