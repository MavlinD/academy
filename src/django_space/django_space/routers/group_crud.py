from asgiref.sync import sync_to_async
from django.contrib.auth.models import Group, User
from fastapi import Depends, status
from fastapi_users.router.common import ErrorModel
from logrich.logger_ import log  # noqa
from pydantic import BaseModel

from src.auth.assets import APIRouter
from src.auth.handlers.errors.codes import ErrorCodeLocal
from src.auth.schemas.group import GroupAttr, GroupCreate
from src.auth.schemas.request import ActionsType, GroupRename, UserGroupMove
from src.auth.schemas.scheme_tools import get_qset
from src.auth.schemas.token import GroupScheme, UserScheme
from src.auth.schemas.user import UserAttr
from src.auth.users.dependencies import get_current_active_superuser, get_group_or_404
from src.auth.users.group_manager import GroupManager
from src.auth.users.init import get_group_manager, get_user_manager
from src.auth.users.user_manager import UserManager

router = APIRouter()


@router.put(
    "/create",
    response_model=GroupScheme,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_superuser)],
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
async def create_group(
    groupname: GroupCreate,
    group_manager: GroupManager = Depends(get_group_manager),
) -> GroupScheme:
    """Создать или вернуть группу"""
    resp = await group_manager.create(groupname)
    return resp


@router.patch(
    "",
    response_model=GroupScheme,
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
async def rename_group(
    payload: GroupRename,
    group_manager: GroupManager = Depends(get_group_manager),
) -> GroupScheme:
    """Переименовать группу по имени или id"""
    # log.debug(payload)
    resp = await group_manager.update(payload)
    return resp


@router.patch(
    "/{action:str}",
    response_model=UserScheme,
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
async def move_in_out_group(
    action: ActionsType,
    params: UserGroupMove,
    group_manager: GroupManager = Depends(get_group_manager),
    user_manager: UserManager = Depends(get_user_manager),
) -> User:
    """Переместить пользователя (по имени, email или id) в/из группы (по имени или id)"""
    user = await user_manager.get_user_by_uniq_attr(UserAttr(attr=params.user_attr))
    group = await group_manager.get_group_by_uniq_attr(GroupAttr(attr=params.group_attr))
    if user and group:
        match action:
            case action.add:
                await sync_to_async(user.groups.add)(group)
            case action.remove:
                await sync_to_async(user.groups.remove)(group)
        return await UserScheme.from_orms(user)


@router.get(
    "/list",
    response_model=list[GroupScheme],
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
async def read_groups(
    group_manager: GroupManager = Depends(get_group_manager),
) -> list[BaseModel]:
    """Получить список групп"""
    groups = await group_manager.get_list_groups()
    resp = await get_qset(qset=groups, model=GroupScheme)
    return resp


@router.get(
    "/{group_attr:str}",
    response_model=GroupScheme,
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
async def read_group(
    group: Group = Depends(get_group_or_404),
) -> GroupScheme:
    """Получить группу по имени или id"""
    # log.debug(group)
    return group


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
async def delete_group(
    group_manager: GroupManager = Depends(get_group_manager),
    group: Group = Depends(get_group_or_404),
) -> None:
    """Удалить группу по имени или id"""
    await group_manager.delete(group)
