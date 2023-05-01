from fastapi import FastAPI

from src.auth.config import config
from src.django_space.ads.routers.ad_crud import router as ad_crud

prefix = config.API_PATH_PREFIX
__version__ = config.API_VERSION


def init_ads_router(app: FastAPI) -> None:
    """order is important !!!"""
    ...
    app.include_router(ad_crud, prefix=f"{prefix}{__version__}/ads", tags=["CRUD for Ads"])

    # app.include_router(home, prefix="")
