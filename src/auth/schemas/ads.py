from __future__ import annotations

from typing import Annotated

from asgiref.sync import sync_to_async
from djantic import ModelSchema
from fastapi import Body
from logrich.logger_ import log  # noqa
from pydantic import BaseModel, Field
from pydantic.types import Decimal

from src.django_space.ads.config import config
from src.django_space.ads.models import Ads, Image

constrain_ad_name = Body(
    title="Имя объявления",
    min_length=config.AD_NAME_MIN_LENGTH,
    max_length=config.AD_NAME_MAX_LENGTH,
)

constrain_ad_desc = Body(
    title="Описание объявления",
    min_length=config.AD_DESC_MIN_LENGTH,
    max_length=config.AD_DESC_MAX_LENGTH,
)

constrain_price = Field(title="Цена", max_digits=config.AD_MAX_PRICE_DIGITS, decimal_places=2)


class AdCreate(BaseModel):
    """Схема для создания объявления"""

    name: str = constrain_ad_name
    desc: str = constrain_ad_desc
    price: Annotated[Decimal, constrain_price]


class AdUpdate(BaseModel):
    """Схема для обновления объявления"""

    name: Annotated[str | None, constrain_ad_name] = None
    desc: Annotated[str | None, constrain_ad_desc] = None
    price: Annotated[Decimal | None, constrain_price] = None


class AdAttr(BaseModel):
    """Схема для валидации параметров внутри приложения"""

    attr: str | int = constrain_ad_name


class ImageSchemeWithoutAds(ModelSchema):
    """Схема для списка изображений."""

    class Config:
        model = Image
        include = ["id", "path", "is_main"]


class AdScheme(ModelSchema):
    """Общая схема объявления"""

    image_set: list[ImageSchemeWithoutAds] = []

    class Config:
        model = Ads
        include = ["id", "name", "price", "desc", "image_set"]

    @classmethod
    async def from_orms(cls, v):
        """reload from_orm method"""
        return await sync_to_async(cls.from_orm)(v)
