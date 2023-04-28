import typing

from django.contrib.auth.models import Group
from fastapi import Depends, HTTPException
from fastapi.params import Path
from fastapi.security import OAuth2PasswordBearer
from logrich.logger_ import log  # noqa
from sqlalchemy.exc import StatementError
from starlette import status

from src.auth.config import config
from src.auth.schemas.group import GroupAttr, constrain_group_path
from src.auth.schemas.token import UserScheme
from src.auth.schemas.user import UserAttr
from src.auth.users.exceptions import UserNotExists
from src.auth.users.group_manager import GroupManager
from src.auth.users.init import get_group_manager, get_user_manager
from src.auth.users.user_manager import UserManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config.API_PATH_PREFIX}{config.API_VERSION}/auth/token-obtain")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_manager: UserManager = Depends(get_user_manager),
) -> UserScheme | None:
    """Зависимость, возвращает текущего пользователя из токена в заголовке запроса"""
    user = await user_manager.jwt_verify(token=token)
    return user


async def get_current_active_user(
    user: UserScheme = Depends(get_current_user),
) -> UserScheme | None:
    """Зависимость, возвращает текущего пользователя из токена в заголовке запроса"""
    if user.is_active:
        return user
    raise HTTPException(status_code=401, detail="Inactive user.")


async def get_current_active_superuser(
    user: UserScheme = Depends(get_current_user),
) -> UserScheme | None:
    """Зависимость, возвращает текущего суперпользователя из токена в заголовке запроса"""
    if user:
        if user.is_superuser:
            return user
    raise HTTPException(status_code=403, detail="Not a superuser.")


@typing.no_type_check
async def get_user_or_404(
    user_attr: str = Path(
        ...,
        min_length=1,
        max_length=config.USERNAME_ATTR_MAX_LENGTH,
        description="username/email/ID пользователя",
    ),
    user_manager: UserManager = Depends(get_user_manager),
) -> UserScheme:
    """DI of FastAPI, mypy not correct check"""
    try:
        user_attr_ = UserAttr(attr=user_attr.user_attr)
        user = await user_manager.get_user_by_uniq_attr(user_attr_)
        return user
    except UserNotExists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except StatementError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.args)


@typing.no_type_check
async def get_group_or_404(
    group_attr: str = constrain_group_path,
    group_manager: GroupManager = Depends(get_group_manager),
) -> Group:
    """DI of FastAPI, mypy not correct check"""
    group = await group_manager.get_group_by_uniq_attr(group_attr=GroupAttr(attr=group_attr))
    return group
