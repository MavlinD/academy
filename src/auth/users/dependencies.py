from django.contrib.auth.models import User
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.users.init import get_user_manager
from src.auth.users.user_manager import UserManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config.API_PATH_PREFIX}{config.API_VERSION}/auth/token-obtain")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_manager: UserManager = Depends(get_user_manager),
) -> User:
    """Зависимость, возвращает текущего пользователя из токена в заголовке запроса"""
    user = await user_manager.jwt_verify(token=token)
    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """Зависимость, возвращает активного текущего пользователя из токена в заголовке запроса"""
    if user.is_active:
        return user
    raise HTTPException(status_code=401, detail="Inactive user.")


async def get_current_active_superuser(
    user: User = Depends(get_current_active_user),
) -> User:
    """Зависимость, возвращает текущего суперпользователя из токена в заголовке запроса"""
    if user:
        if user.is_superuser:
            return user
    raise HTTPException(status_code=403, detail="Not a superuser or not active user.")
