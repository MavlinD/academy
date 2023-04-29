from django.contrib.auth.models import User
from fastapi import Depends, status
from fastapi_users.router.common import ErrorModel
from logrich.logger_ import log  # noqa

from src.auth.assets import APIRouter
from src.auth.handlers.errors.codes import ErrorCodeLocal
from src.auth.schemas.token import UserScheme
from src.auth.schemas.user import UserCreate, UserUpdate
from src.auth.users.dependencies import get_current_active_superuser
from src.auth.users.init import get_user_manager
from src.auth.users.user_manager import UserManager
from src.django_space.django_space import adapters

router = APIRouter()


@router.get(
    "/{user_attr:str}",
    response_model=UserScheme,
    dependencies=[Depends(get_current_active_superuser)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
    },
)
async def read_user(
    user: User = Depends(adapters.retrieve_users),
) -> UserScheme:
    """Получить пользователя по имени, почте или id"""
    # log.debug(user)
    resp = await UserScheme.from_orms(user)
    return resp


@router.patch(
    "/{user_attr:str}",
    response_model=UserScheme,
    dependencies=[Depends(get_current_active_superuser)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCodeLocal.GROUP_NOT_FOUND: {
                            "summary": "A group with this name not exists.",
                            "value": {"detail": ErrorCodeLocal.GROUP_NOT_FOUND},
                        },
                        ErrorCodeLocal.USER_NOT_FOUND: {
                            "summary": "A user with this name not exists.",
                            "value": {"detail": ErrorCodeLocal.USER_NOT_FOUND},
                        },
                    }
                }
            },
        },
    },
)
async def update_user(
    user_update: UserUpdate,
    user: User = Depends(adapters.retrieve_users),
    user_manager: UserManager = Depends(get_user_manager),
) -> UserScheme:
    """
    Обновить пользователя по имени, почте или id.<br>
    Если обновляется **email**, то пользователь сможет войти после того как верифицирует новый адрес.
    """
    # log.debug(user)
    user_update.username = user.username
    # log.debug(user_update)
    resp = await user_manager.update_user_in_db(user=user, **user_update.dict(exclude_unset=True, exclude_none=True))
    return resp
    # log.debug(ret)
    # ret = UserScheme.from_orm(user)
    # return ret


@router.put(
    "/create",
    response_model=UserScheme,
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
                        ErrorCodeLocal.USER_ALREADY_EXISTS: {
                            "summary": "A user with this email or username already exists.",
                            "value": {"detail": ErrorCodeLocal.USER_ALREADY_EXISTS},
                        },
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCodeLocal.GROUP_NOT_FOUND: {
                            "summary": "A group with this name not found.",
                            "value": {"detail": ErrorCodeLocal.GROUP_NOT_FOUND},
                        },
                    }
                }
            },
        },
    },
)
async def create_user(
    user_create: UserCreate,
    user_manager: UserManager = Depends(get_user_manager),
) -> UserScheme:
    """Создать пользователя"""
    user = await user_manager.put_user_in_db(**user_create.dict(exclude={"groups"}, exclude_unset=True))
    return user


@router.delete(
    "/{user_attr:str}",
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
            "description": "The user does not exist.",
        },
    },
)
async def delete_user(
    user: User = Depends(adapters.retrieve_users),
    user_manager: UserManager = Depends(get_user_manager),
) -> None:
    """Удалить пользователя по имени, почте или id"""
    await user_manager.remove_user(user=user)
