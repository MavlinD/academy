from fastapi import FastAPI

from src.auth.config import config
from src.django_space.django_space.routers.home import router as home
from src.django_space.django_space.routers.jwt_obtain import router as jwt_obtain
from src.django_space.django_space.routers.jwt_refresh import router as jwt_refresh
from src.django_space.django_space.routers.jwt_verify import router as jwt_verify

prefix = config.API_PATH_PREFIX
__version__ = config.API_VERSION


def init_base_router(app: FastAPI) -> None:
    """order is important !!!"""

    app.include_router(jwt_obtain, prefix=f"{prefix}{__version__}/auth", tags=["JWT"])
    app.include_router(jwt_refresh, prefix=f"{prefix}{__version__}/auth", tags=["JWT"])
    app.include_router(jwt_verify, prefix=f"{prefix}{__version__}/auth", tags=["JWT"])

    app.include_router(home, prefix="")
