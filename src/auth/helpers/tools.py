import locale

from fastapi import FastAPI
from httpx import Request
from logrich.logger_ import log  # noqa

from src.auth.config import config

locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")


def print_endpoints(app: FastAPI) -> None:
    """печать всех доступных конечных точек"""
    log.debug(type(app.routes))
    for rout in app.routes:
        log.info(
            f"[#EE82EE]{str(next(iter(rout.methods))) + ':':<7}[/][#ADFF2F]"  # type: ignore
            f"{rout.path}:[/] [#FF4500]{rout.name}[/]"
        )


async def print_request(request: Request) -> None:
    """
    исп-ю в тестах
    https://www.python-httpx.org/api/
    """
    log.info(f"[#EE82EE]{str(request.method) + ':':<8}[/]{request.url.raw_path.decode('UTF-8')}")


def show_dbs_engine() -> str | None:
    """return canonic DBS engine name"""
    match config.DBS_ENGINE:
        case "sqlite":
            return "SQLite"
        case "postgres":
            return "PostgreSQL"

    return None
