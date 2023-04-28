from typing import Callable

import sqlalchemy
from fastapi import FastAPI, Request, Response
from logrich.logger_ import log  # noqa
from starlette.middleware.cors import CORSMiddleware


def init_middleware(app: FastAPI) -> None:
    """middleware"""
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # @app.middleware("http")
    async def db_session_middleware(request: Request, call_next: Callable) -> Response:
        try:
            log.trace(sqlalchemy.__version__)
            response = await call_next(request)
            # request.state.db = get_async_session()
            # log.trace(request.state.db)
            # log.info(response)
            # log.debug(dir(request.state.db))
        finally:
            ...
            # await request.state.db.aclose()
        return response
