import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Annotated, Optional

import django
import pydantic
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from djantic import ModelSchema
from fastapi import Body
from logrich.logger_ import log  # noqa
from pydantic import BaseModel, EmailStr, Field, validator

from src.auth.config import config
from src.auth.schemas.group import GroupOut


class AccessToken(BaseModel):
    """Access token details"""

    access_token: str


class RefreshToken(AccessToken):
    """Access and refresh token details"""

    refresh_token: str


class TokenType(str, Enum):
    """Перечисление возможных типов токенов"""

    access = "access"
    refresh = "refresh"


class TokenExpiration(BaseModel):
    """Примесь для пользовательских токенов"""

    type: str
    days: int
    hours: Annotated[int, Field(le=24)]
    minutes: Annotated[int, Field(le=60)]

    @pydantic.root_validator()
    def days_of_type(cls, v: dict) -> dict:
        # log.debug("", o=v)
        if v["type"] == "access" and v["days"] > 1:
            raise ValueError(f"Дни годности аксесс токена не могут превышать 1 дня, передано: {v}")
        if v["type"] == "refresh" and v["days"] > config.JWT_REFRESH_KEY_EXPIRES_TIME_DAYS:
            raise ValueError(
                f"Дни годности рефреш токена не могут превышать {config.JWT_REFRESH_KEY_EXPIRES_TIME_DAYS} "
                f"дня, передано: {v}"
            )

        return v


class TokenModelForGenerate(TokenExpiration):
    """Схема токена для генерации, исп-ся до создания токена для записи"""

    sub: str = "auth"
    uid: int
    username: str
    email: EmailStr
    first_name: str | None
    last_name: str | None
    is_superuser: bool = False
    is_staff: bool = False
    is_active: bool = False
    aud: str | list[str] | None
    groups: list

    class Config:
        orm_mode = True
        use_enum_values = True


class AccessTokenModelForWrite(BaseModel):
    """Схема для записи в ответ"""

    sub: str = config.TOKEN_SUB
    username: str
    uid: int
    type: str = "access"
    email: EmailStr
    first_name: str | None
    last_name: str | None
    is_superuser: bool = False
    is_staff: bool = False
    is_active: bool = False
    groups: list[GroupOut] = []

    @validator("type")
    def type_must_be_access(cls, v: str) -> str:
        if v != "access":
            raise ValueError("Token must be the access type!")
        return v

    iss: str = config.TOKEN_ISS
    jti: Annotated[str, Field(default_factory=lambda: uuid.uuid4().hex)]
    iat: datetime = datetime.utcnow()
    exp: datetime = datetime.utcnow() + timedelta(minutes=config.JWT_ACCESS_KEY_EXPIRES_TIME_MINUTES)
    aud: str | list[str]


class RefreshTokenModelForWrite(BaseModel):
    sub: str = "auth"
    uid: int
    type: str = "refresh"

    @validator("type")
    def type_must_be_refresh(cls, v: str) -> str:
        if v != "refresh":
            raise ValueError("Token must be the refresh type!")
        return v

    iss: str = config.TOKEN_ISS
    jti: Annotated[str, Field(default_factory=lambda: uuid.uuid4().hex)]
    iat: datetime = datetime.utcnow()
    exp: datetime = datetime.utcnow() + timedelta(days=config.JWT_REFRESH_KEY_EXPIRES_TIME_DAYS)
    aud: Optional[str]


class TokensPair(BaseModel):
    """Модель для пары токенов, access & refresh"""

    access_token: str
    refresh_token: str


class TokenRequest(BaseModel):
    """Схема для верификации запроса с токеном"""

    token: str = Body(max_length=3000)


class UserSchemeWithoutGroups(ModelSchema):
    """Схема для списка пользователей, без групп, чтобы избежать цикличный ссылок."""

    class Config:
        model = django.contrib.auth.models.User
        include = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_superuser",
            "is_staff",
            "is_active",
        ]


class GroupScheme(ModelSchema):
    """Общая схема группы"""

    user_set: list[UserSchemeWithoutGroups] = []

    class Config:
        model = Group
        include = ["id", "name", "user_set"]


class GroupSchemeWithoutUsers(ModelSchema):
    """Схема группы для вывода в составе списка пользователей,
    не включает пользователей, тк здесь это избыточно"""

    class Config:
        model = Group
        include = ["id", "name"]


class UserScheme(ModelSchema):
    groups: list[GroupSchemeWithoutUsers] = []

    class Config:
        model = get_user_model()
        include = [
            "id",
            "email",
            "username",
            "groups",
            "first_name",
            "last_name",
            "is_superuser",
            "is_staff",
            "is_active",
        ]

    @classmethod
    async def from_orms(cls, v):
        """reload from_orm method"""
        return await sync_to_async(cls.from_orm)(v)
