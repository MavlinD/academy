from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse
from logrich.logger_ import log  # noqa
from yarl import URL

from src.auth.assets import APIRouter
from src.auth.config import templates

router = APIRouter()


@router.get("/", include_in_schema=False, response_class=HTMLResponse)
async def read_home(request: Request) -> Any:
    """домашняя страница"""
    log.debug(request)
    return templates.TemplateResponse("index.html", {"request": request})


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
