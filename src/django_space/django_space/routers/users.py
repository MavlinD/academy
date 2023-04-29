from asgiref.sync import sync_to_async, async_to_sync
from django.db.models import Manager, QuerySet, Model
from fastapi import Depends, Query
from fastapi_pagination import Page, Params
from fastapi_pagination import paginate as paginate_
from fastapi_pagination.bases import AbstractPage
from logrich.logger_ import log  # noqa
from pydantic import BaseModel

from src.auth.assets import APIRouter
from src.auth.config import config
from src.auth.schemas.request import UsersFilter
from src.auth.schemas.scheme_tools import get_qset
from src.auth.schemas.token import UserScheme
from src.auth.users.dependencies import get_current_active_superuser
from src.auth.users.init import get_user_manager
from src.auth.users.my_paginate import PageForPost
from src.auth.users.router.responses import responses
from src.auth.users.user_manager import UserManager

router = APIRouter()


@router.get(
    "/v1",
    response_model=list[UserScheme],
    dependencies=[Depends(get_current_active_superuser)],
    responses=responses,
)
async def list_of_users(
    username: str = Query(
        None,
        min_length=config.USERNAME_ATTR_MIN_LENGTH,
        max_length=config.USERNAME_ATTR_MAX_LENGTH,
        description="любая часть \\<username> пользователя",
    ),
    email: str = Query(
        None,
        min_length=config.USERNAME_ATTR_MIN_LENGTH,
        max_length=config.USERNAME_ATTR_MAX_LENGTH,
        description="любая часть \\<email> пользователя",
    ),
    first_name: str = Query(
        None,
        min_length=config.USERNAME_ATTR_MIN_LENGTH,
        max_length=config.USERNAME_ATTR_MAX_LENGTH,
        description="любая часть <first_name> пользователя",
    ),
    last_name: str = Query(
        None,
        min_length=config.USERNAME_ATTR_MIN_LENGTH,
        max_length=config.USERNAME_ATTR_MAX_LENGTH,
        description="любая часть <last_name> пользователя",
    ),
    is_superuser: bool = Query(None, description="is superuser?"),
    is_active: bool = Query(None, description="is active?"),
    is_staff: bool = Query(None, description="is staff?"),
    user_manager: UserManager = Depends(get_user_manager),
) -> list[BaseModel]:
    """получить список пользователей"""
    params = UsersFilter(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_superuser=is_superuser,
        is_staff=is_staff,
        is_active=is_active,
    )
    # log.debug(params)

    users = await user_manager.list_users_v2(params=params)
    resp = await get_qset(qset=users, model=UserScheme)
    return resp


@router.get(
    "/v2",
    response_model=Page[UserScheme],
    dependencies=[Depends(get_current_active_superuser)],
    responses=responses,
)
async def list_of_users_get(
    search: str = Query(
        None,
        min_length=config.USERNAME_ATTR_MIN_LENGTH,
        max_length=config.USERNAME_ATTR_MAX_LENGTH,
        description="любая часть **\\<username> <email> <first_name> <last_name>** пользователя.",
    ),
    is_staff: bool = Query(None, description="is staff?"),
    is_superuser: bool = Query(None, description="is superuser?"),
    is_active: bool = Query(None, description="is active?"),
    user_manager: UserManager = Depends(get_user_manager),
) -> AbstractPage[BaseModel]:
    """получить список пользователей с пагинацией, вызванный без параметров вернет всех пользователей"""
    # https://uriyyo-fastapi-pagination.netlify.app/advanced/
    params = UsersFilter(
        search=search,
        is_superuser=is_superuser,
        is_staff=is_staff,
        is_active=is_active,
    )
    users = await user_manager.list_users_v2(params=params)
    resp = await get_qset(qset=users, model=UserScheme)
    return paginate_(list(resp))


@router.post(
    "",
    response_model=PageForPost[UserScheme],
    dependencies=[Depends(get_current_active_superuser)],
    responses=responses,
)
async def list_of_users_post(
    payload: UsersFilter = UsersFilter(),
    paginate: Params = Params(),
    user_manager: UserManager = Depends(get_user_manager),
) -> AbstractPage[BaseModel]:
    """получить список пользователей с пагинацией, вызванный без параметров вернет всех пользователей"""
    # https://uriyyo-fastapi-pagination.netlify.app/advanced/

    params = UsersFilter(
        search=payload.search,
        is_superuser=payload.is_superuser,
        is_active=payload.is_active,
        is_staff=payload.is_staff,
        users=payload.users,
        groups=payload.groups,
    )

    users = await user_manager.list_users_v2(params=params)
    resp = await get_qset(qset=users, model=UserScheme)
    return paginate_(list(resp), params=paginate)
    # return paginate_(list(users), params=paginate)
