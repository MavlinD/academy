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
from src.django_space.ads.models import Ads, Image


class ImageCreate(BaseModel):
    """Схема для создания изображения"""

    path: str
    ads_id: int


# class ImageAttr(BaseModel):
#     """Схема для валидации параметров внутри приложения"""
#
#     attr: str | int = constrain_ad_name


class ImageOut(BaseModel):
    """Схема для вывода групп в разрезе пользователей"""

    name: str
    ads_id: int
    id: str

    class Config:
        orm_mode = True


class AdSchemeWithoutImages(ModelSchema):
    """Схема для списка изображений."""

    class Config:
        model = Ads
        # include = [
        #     "id",
        #     "name",
        #     "desc",
        #     "price",
        # ]


class ImageScheme(ModelSchema):
    """Общая схема объявления"""

    # ads_id: list[AdSchemeWithoutImages] = []
    ads_id: AdSchemeWithoutImages

    class Config:
        model = Image
        # include = ["id", "path", "ads_id"]

    @classmethod
    async def from_orms(cls, v):
        """reload from_orm method"""
        return await sync_to_async(cls.from_orm)(v)
