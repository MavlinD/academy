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

    path: str = Body(max_length=256)
    is_main: bool = False


class ImageScheme(ModelSchema):
    """Общая схема объявления"""

    class Config:
        model = Image

    @classmethod
    async def from_orms(cls, v):
        """reload from_orm method"""
        return await sync_to_async(cls.from_orm)(v)
