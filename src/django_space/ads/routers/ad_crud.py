from asgiref.sync import sync_to_async
from django.contrib.auth.models import Group, User
from fastapi import Depends, status
from fastapi_users.router.common import ErrorModel
from logrich.logger_ import log  # noqa
from pydantic import BaseModel

from src.auth.assets import APIRouter
from src.auth.handlers.errors.codes import ErrorCodeLocal
from src.auth.schemas.ads import AdCreate, AdRename, AdScheme
from src.auth.schemas.group import GroupAttr, GroupCreate
from src.auth.schemas.request import ActionsType, GroupRename, UserGroupMove
from src.auth.schemas.scheme_tools import get_qset
from src.auth.schemas.token import GroupScheme, UserScheme
from src.auth.schemas.user import UserAttr
from src.auth.users.ads_manager import AdManager
from src.auth.users.dependencies import (
    get_current_active_superuser,
    get_current_active_user,
    get_group_or_404,
)
from src.auth.users.group_manager import GroupManager
from src.auth.users.init import get_ads_manager, get_group_manager, get_user_manager
from src.auth.users.user_manager import UserManager
from src.django_space.ads.models import Ads

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
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
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
    ad_name: AdCreate,
    ad_manager: AdManager = Depends(get_ads_manager),
) -> AdScheme:
    """Создать или вернуть группу"""
    resp = await ad_manager.create(ad_create=ad_name)
    # log.debug(ad_name)
    # log.debug(resp)
    return resp


@router.patch(
    "",
    response_model=AdScheme,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
        },
    },
)
async def rename_ad(
    payload: AdRename,
    group_manager: AdManager = Depends(get_group_manager),
) -> AdScheme:
    """Переименовать группу по имени или id"""
    group = await group_manager.update(payload)
    resp = await AdScheme.from_orms(group)
    return resp


@router.get(
    "/list",
    response_model=list[AdScheme],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
        },
    },
)
async def read_ads(
    group_manager: AdManager = Depends(get_group_manager),
) -> list[BaseModel]:
    """Получить список групп"""
    groups = await group_manager.get_list_groups()
    resp = await get_qset(qset=groups, model=AdScheme)
    return resp


@router.get(
    "/{group_attr:str}",
    response_model=AdScheme,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
        },
    },
)
async def read_ad(
    group: Ads = Depends(get_group_or_404),
) -> AdScheme:
    """Получить группу по имени или id"""
    resp = await AdScheme.from_orms(group)
    return resp


@router.delete(
    "/{group_attr:str}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_superuser)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The group does not exist.",
        },
    },
)
async def delete_ad(
    group_manager: AdManager = Depends(get_group_manager),
    group: Ads = Depends(get_group_or_404),
) -> None:
    """Удалить группу по имени или id"""
    await group_manager.delete(group)
