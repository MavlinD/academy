from fastapi import Depends, status
from fastapi_pagination import Page, Params
from fastapi_pagination import paginate as paginate_
from fastapi_pagination.bases import AbstractPage
from logrich.logger_ import log  # noqa
from pydantic import BaseModel, Field

from src.auth.assets import APIRouter
from src.auth.schemas.ads import AdCreate, AdScheme
from src.auth.schemas.scheme_tools import get_qset
from src.auth.users.ads_manager import AdManager
from src.auth.users.dependencies import get_current_active_user
from src.auth.users.init import get_ads_manager
from src.auth.users.my_paginate import PageForPost
from src.django_space.ads.models import Ads
from src.django_space.django_space.adapters import retrieve_ad
from src.django_space.django_space.routers.jwt_obtain import unauthorized_responses

router = APIRouter()


@router.put(
    "/create",
    response_model=AdScheme,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
    responses={
        **unauthorized_responses,
    },
)
async def create_ad(
    ad: AdCreate,
    ad_manager: AdManager = Depends(get_ads_manager),
) -> AdScheme:
    """Создать или вернуть группу"""
    resp = await ad_manager.create(ad_create=ad)
    return resp


@router.patch(
    "/{ad_attr:str}",
    response_model=AdScheme,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_user)],
    responses={
        **unauthorized_responses,
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


# параметры пагинации по умолчанию
Page = Page.with_custom_options(
    size=Field(10, ge=1, le=15),
)


@router.get(
    "/list",
    response_model=Page[AdScheme],
    status_code=status.HTTP_200_OK,
    responses={
        **unauthorized_responses,
    },
)
async def read_ads(
    ad_manager: AdManager = Depends(get_ads_manager),
) -> AbstractPage[BaseModel]:
    """Получить список объявлений"""
    ads = await ad_manager.get_list_ads()
    resp = await get_qset(qset=ads, model=AdScheme)
    return paginate_(list(resp))


@router.get(
    "/{ad_attr:str}",
    response_model=AdScheme,
    status_code=status.HTTP_200_OK,
    responses={
        **unauthorized_responses,
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
        **unauthorized_responses,
        status.HTTP_404_NOT_FOUND: {
            "description": "Объявление не найдено.",
        },
    },
)
async def delete_ad(
    ad: Ads = Depends(retrieve_ad),
    ad_manager: AdManager = Depends(get_ads_manager),
) -> None:
    """Удалить объявление по id"""
    await ad_manager.delete(ad)
