import re
import urllib.request
from pathlib import Path
from pprint import pprint  # noqa
from typing import Any, Callable, Dict

import toml
from fastapi import APIRouter as FastAPIRouter
from fastapi.types import DecoratedCallable


class APIRouter(FastAPIRouter):
    """compute trailing slashes in request"""

    def api_route(
        self, path: str, *, include_in_schema: bool = True, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        if path.endswith("/") and path != "/":
            path = path[:-1]

        add_path = super().api_route(path, include_in_schema=include_in_schema, **kwargs)
        alternate_path = path + "/"
        add_alternate_path = super().api_route(alternate_path, include_in_schema=False, **kwargs)

        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            add_path(func)
            return add_alternate_path(func)

        return decorator


def get_project() -> Dict:
    """return project file"""
    pyproject = toml.load(Path("pyproject.toml"))
    return pyproject["tool"]["poetry"]


def get_key(key: str) -> str:
    """получим ключ из файла на диске"""
    with open(Path(f"{key}"), mode="r", encoding="utf-8") as f:
        return f.read().strip()


async def update_version_badge() -> None:
    """обновляет бейдж версии"""
    pyproject = toml.load(Path("pyproject.toml"))
    VERSION = pyproject["tool"]["poetry"]["version"]
    content = (
        f"https://img.shields.io/badge/version-{VERSION}-%230071C5?style=for-the-badge&logo=semver&logoColor=orange"
    )
    await update_badge(search=r"\[version-badge\]: .*", content=f"[version-badge]: {content}")


async def get_test_status_badge(status: int) -> None:
    """обновляет бейдж статуса тестов"""
    match status:
        case 0:
            text = "passed"
            color = "green"
        case _:
            text = "failed"
            color = "red"

    content = f"https://img.shields.io/badge/test-{text}-{color}?style=for-the-badge&logo=pytest&logoColor=orange"
    await update_badge(search=r"\[tests-status-badge\]: .*", content=f"[tests-status-badge]: {content}")


async def fetch_badges(badge_name: str, text: str, color: str, badge_logo: str, badge_file_name: str) -> None:
    """получает указанный бейдж, not used"""
    # https://img.shields.io/badge/tests-passed-green?style=for-the-badge&logo=gitlab&logoColor=orange
    bage_url = (
        f"https://img.shields.io/badge/{badge_name}-{text}-{color}?style=for-the-badge"
        f"&logo={badge_logo}&logoColor=orange"
    )
    # log.debug(bage_url)
    user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"
    headers = {"User-Agent": user_agent}
    req = urllib.request.Request(bage_url, headers=headers)

    with urllib.request.urlopen(req) as response:
        content = response.read().decode("utf-8")
        await write_file(content=content, file_name=f"../{badge_file_name}-badge.svg")


async def write_file(content: str, file_name: str = "temp.txt") -> None:
    """записывает в файл переданный контент"""
    with open(Path(file_name), "w", encoding="utf-8") as fp:
        fp.write(content)


async def update_badge(search: str, content: str, file_name: str = "README.md") -> str:
    """обновляет ссылки на бейджи"""

    with open(Path(file_name), "r", encoding="utf-8") as fp:
        file_content = fp.read()
        new_content = re.sub(search, content, file_content)

    with open(Path(file_name), "w", encoding="utf-8") as fw:
        fw.write(new_content)

    return new_content
