from typing import Type, TypeVar

from django.contrib.auth.models import User
from django.db import models
from fastapi import Depends, HTTPException, Path
from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.schemas.user import UserAttr
from src.auth.users.init import get_user_manager
from src.auth.users.user_manager import UserManager

ModelT = TypeVar("ModelT", bound=models.Model)


async def retrieve_users(
    user_attr: str = Path(
        min_length=1,
        max_length=config.USERNAME_ATTR_MAX_LENGTH,
        description="username, email, ID пользователя",
    ),
    user_manager: UserManager = Depends(get_user_manager),
) -> User:
    attr = UserAttr(attr=user_attr)
    # log.trace(attr)
    user: User = await user_manager.get_user_by_uniq_attr(user_attr=attr)
    return user
