from asgiref.sync import sync_to_async
from fastapi import Depends, Path, status
from fastapi_users.router.common import ErrorModel
from logrich.logger_ import log  # noqa
from pydantic import BaseModel

from src.auth.assets import APIRouter
from src.auth.handlers.errors.codes import ErrorCodeLocal
from src.auth.schemas.ads import AdAttr, AdCreate, AdScheme
from src.auth.schemas.scheme_tools import get_qset
from src.auth.users.ads_manager import AdManager
from src.auth.users.dependencies import get_current_active_user
from src.auth.users.init import get_ads_manager
from src.django_space.ads.config import config
from src.django_space.ads.models import Ads
from src.django_space.django_space.adapters import retrieve_ad

router = APIRouter()


@router.put(
    "/create",
    response_model=AdScheme,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCodeLocal.GROUP_ALREADY_EXISTS: {
                            "summary": "A group with this name already exists.",
                            "value": {"detail": ErrorCodeLocal.GROUP_ALREADY_EXISTS},
                        },
                    }
                }
            },
        },
    },
)
async def create_ad(
    ad: AdCreate,
    ad_manager: AdManager = Depends(get_ads_manager),
) -> AdScheme:
    """Создать или вернуть группу"""
    log.debug(ad)
    resp = await ad_manager.create(ad_create=ad)
    # log.debug(ad_name)
    # log.debug(resp)
    return resp


@router.patch(
    "/{ad_attr:str}",
    response_model=AdScheme,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_user)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
    },
)
async def update_ad(
    payload: AdCreate,
    ad: Ads = Depends(retrieve_ad),
    ad_manager: AdManager = Depends(get_ads_manager),
) -> AdScheme:
    """Обновить объявление по имени или id"""
    ad = await ad_manager.update(ad=ad, payload=payload.dict(exclude_unset=True, exclude_none=True))
    resp = await AdScheme.from_orms(ad)
    return resp


@router.get(
    "/list",
    response_model=list[AdScheme],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
    },
)
async def read_ads(
    ad_manager: AdManager = Depends(get_ads_manager),
) -> list[BaseModel]:
    """Получить список объявлений"""
    ads = await ad_manager.get_list_ads()
    resp = await get_qset(qset=ads, model=AdScheme)
    return resp


@router.get(
    "/{ad_attr:str}",
    response_model=AdScheme,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
    },
)
async def read_ad(
    ad: Ads = Depends(retrieve_ad),
) -> AdScheme:
    """Получить объявление по имени или id"""
    resp = await AdScheme.from_orms(ad)
    return resp


@router.delete(
    "/{ad_attr:str}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_user)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The ad does not exist.",
        },
    },
)
async def delete_ad(
    ad: Ads = Depends(retrieve_ad),
    ad_manager: AdManager = Depends(get_ads_manager),
) -> None:
    """Удалить объявление по id"""
    await ad_manager.delete(ad)
