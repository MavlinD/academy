from fastapi import FastAPI

from src.auth.config import config
from src.django_space.django_space.routers.group_crud import router as group_crud
from src.django_space.django_space.routers.home import router as home
from src.django_space.django_space.routers.jwt_obtain import router as jwt_obtain
from src.django_space.django_space.routers.jwt_refresh import router as jwt_refresh
from src.django_space.django_space.routers.jwt_verify import router as jwt_verify
from src.django_space.django_space.routers.me import router as me
from src.django_space.django_space.routers.password_reset import (
    router as password_reset,
)
from src.django_space.django_space.routers.register import router as register
from src.django_space.django_space.routers.user_crud import router as user_crud
from src.django_space.django_space.routers.user_verify import router as user_verify
from src.django_space.django_space.routers.users import router as users

prefix = config.API_PATH_PREFIX
__version__ = config.API_VERSION


def init_base_router(app: FastAPI) -> None:
    """order is important !!!"""
    # app.include_router(me, prefix=f"{prefix}{__version__}/user/me", tags=["Me"])

    app.include_router(jwt_obtain, prefix=f"{prefix}{__version__}/auth", tags=["JWT"])
    app.include_router(jwt_refresh, prefix=f"{prefix}{__version__}/auth", tags=["JWT"])
    app.include_router(jwt_verify, prefix=f"{prefix}{__version__}/auth", tags=["JWT"])

    # app.include_router(register, prefix=f"{prefix}{__version__}/user", tags=["User"])
    # app.include_router(user_verify, prefix=f"{prefix}{__version__}/user", tags=["User"])
    # app.include_router(password_reset, prefix=f"{prefix}{__version__}/user", tags=["User"])
    #
    # app.include_router(user_crud, prefix=f"{prefix}{__version__}/user", tags=["CRUD for super users"])
    #
    # app.include_router(users, prefix=f"{prefix}{__version__}/users", tags=["Users"])
    # app.include_router(group_crud, prefix=f"{prefix}{__version__}/groups", tags=["Groups"])

    app.include_router(home, prefix="")
