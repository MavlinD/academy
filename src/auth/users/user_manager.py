from typing import Any, List, Optional

import jwt
from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from django.db.models import Q, QuerySet
from fastapi.security import OAuth2PasswordRequestForm
from logrich.logger_ import log  # noqa
from pydantic import EmailStr
from starlette.requests import Request

from src.auth.config import config
from src.auth.helpers.email import (
    send_password_reset_email,
    send_verification_email,
    write_response,
)
from src.auth.schemas.request import EmailSchema, UsersFilter
from src.auth.schemas.token import UserScheme
from src.auth.schemas.user import UserAttr, UserCreate, UserUpdate
from src.auth.users.exceptions import (
    InvalidCredentials,
    InvalidVerifyToken,
    UserInactive,
    UserNotExists,
)
from src.auth.users.security.jwt_tools import SecretType, decode_jwt
from src.auth.users.security.password import PasswordHelper


class UserManager:
    reset_password_token_secret: SecretType = config.PRIVATE_KEY
    reset_password_token_lifetime_seconds: int = config.RESET_PASSWORD_TOKEN_LIFETIME_SECONDS

    verification_token_secret: SecretType = config.PRIVATE_KEY
    verification_token_lifetime_seconds: int = config.VERIFICATION_TOKEN_LIFETIME_SECONDS

    reset_password_token_audience: str = "fastapi-users:reset"
    verification_token_audience: str = config.TOKEN_AUDIENCE_VERIFY
    password_helper: PasswordHelper

    def __init__(
        self,
        password_helper: Any = None,
    ):
        self.user_model = get_user_model()

        if password_helper is None:
            self.password_helper = PasswordHelper()
        else:
            self.password_helper = password_helper  # pragma: no cover

    async def get_user_by_uniq_attr(self, user_attr: UserAttr) -> User | None:
        """get user by uniq user attr"""
        attr = user_attr.attr
        if isinstance(attr, str) and attr.isdigit():
            user_in_db = await self.user_model.objects.filter(pk=attr).afirst()
        else:
            user_in_db = await self.user_model.objects.filter(Q(username=attr) | Q(email=attr)).afirst()
        if not user_in_db:
            raise UserNotExists(user=str(attr))
        return user_in_db

    async def authenticate_user(self, credentials: OAuth2PasswordRequestForm) -> User | None:
        """аутентифицировать пользователя по username or email"""
        user_in_db = await self.get_user_by_uniq_attr(UserAttr(attr=credentials.username))
        if not user_in_db.is_active:  # type: ignore
            raise UserInactive(user=user_in_db)

        user: User = await sync_to_async(authenticate)(
            username=user_in_db.username,  # type: ignore
            password=credentials.password,
        )

        # log.debug(user)
        if not user:
            raise InvalidCredentials(msg=credentials.username)

        return user

    async def jwt_verify(self, token: str) -> User:
        """Validate JWT."""
        try:
            data = decode_jwt(token)
            user_attr = UserAttr(attr=data["uid"])
            user: User = await self.get_user_by_uniq_attr(user_attr=user_attr)
            uid = data.get("uid")
            if uid != user.id:
                raise InvalidVerifyToken(msg=token)
            return user

        except (ValueError, jwt.PyJWTError) as err:
            if hasattr(err, "detail"):
                raise InvalidVerifyToken(msg=getattr(err, "detail"))
            else:
                raise InvalidVerifyToken(msg=err)
