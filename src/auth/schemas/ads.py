from __future__ import annotations

from typing import Annotated, TypeAlias

from asgiref.sync import sync_to_async
from djantic import ModelSchema
from fastapi import Body, Path
from logrich.logger_ import log  # noqa
from pydantic import BaseModel, Field, condecimal
from pydantic.schema import Decimal

from src.django_space.ads.config import config

# from src.auth.config import config
from src.django_space.ads.models import Ads

constrain_ad_name = Body(
    min_length=config.AD_NAME_MIN_LENGTH,
    max_length=config.AD_NAME_MAX_LENGTH,
    description="Имя группы",
)

constrain_ad_desc = Body(
    min_length=config.AD_DESC_MIN_LENGTH,
    max_length=config.AD_DESC_MAX_LENGTH,
    description="Описание группы",
)


class AdCreate(BaseModel):
    """Схема для создания группы"""

    name: str = constrain_ad_name
    desc: str = constrain_ad_desc
    price: condecimal(decimal_places=2)


class AdAttr(BaseModel):
    """Схема для валидации параметров внутри приложения"""

    attr: str | int = constrain_ad_name


class AdOut(BaseModel):
    """Схема для вывода групп в разрезе пользователей"""

    name: str
    id: str

    class Config:
        orm_mode = True


class AdSchemeWithoutAds(ModelSchema):
    """Схема для списка пользователей, без групп, чтобы избежать цикличный ссылок."""

    class Config:
        model = Ads
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


class AdScheme(ModelSchema):
    """Общая схема объявления"""

    user_set: list[AdSchemeWithoutAds] = []

    class Config:
        model = Ads
        include = ["id", "name", "price", "desc"]

    @classmethod
    async def from_orms(cls, v):
        """reload from_orm method"""
        return await sync_to_async(cls.from_orm)(v)
