from __future__ import annotations

from asgiref.sync import sync_to_async
from djantic import ModelSchema
from fastapi import Body, Path
from logrich.logger_ import log  # noqa
from pydantic import BaseModel

from src.auth.config import config
from src.django_space.ads.models import Ads

# regex_create = r"^[a-z]+[a-z0-9-]*$(?i)"
# форма записи указанная выше также работает, но выводит НЕ корретный ответ -
# подсказку каким регекспом обрабатывается запрос и inline flag для юникода в python не реализован
# такая форма записи выводит корретный ответ
regex_create = r"^[A-Za-zа-яА-Я]+[A-Za-zа-яА-Я0-9-\s]*$"
# два регеэкспа тк запрос может быть выполнен по ID группы
regex_read = r"^[A-Za-zа-яА-Я0-9-\s]*$"


constrain_ad = Body(
    min_length=config.GROUP_MIN_LENGTH,
    max_length=config.GROUP_MAX_LENGTH,
    description="Имя группы",
    regex=regex_create,
)

constrain_ad_path = Path(
    min_length=1,
    max_length=config.GROUP_MAX_LENGTH,
    description="Имя или ID группы",
    regex=regex_read,
)


class AdCreate(BaseModel):
    """Схема для создания группы"""

    name: str = ""
    desc: str = ""
    # name: str = constrain_ad
    # desc: str = constrain_ad
    price: int = 0


class AdAttr(BaseModel):
    """Схема для валидации параметров внутри приложения"""

    attr: str | int = constrain_ad_path


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
    """Общая схема группы"""

    user_set: list[AdSchemeWithoutAds] = []

    class Config:
        model = Ads
        include = ["id", "name", "price", "desc"]

    @classmethod
    async def from_orms(cls, v):
        """reload from_orm method"""
        return await sync_to_async(cls.from_orm)(v)


# class AdSchemeWithoutAds(ModelSchema):
#     """Схема группы для вывода в составе списка пользователей,
#     не включает пользователей, тк здесь это избыточно"""
#
#     class Config:
#         model = Ads
#         include = ["id", "name"]


class AdRename(BaseModel):
    """Схема параметров запроса на переименование группы"""

    ad: str | int = Body(
        min_length=1,
        max_length=config.GROUP_MAX_LENGTH,
        description="имя/ID группы для изменения",
    )

    new_add_name: str = Body(
        min_length=config.GROUP_MIN_LENGTH,
        max_length=config.GROUP_MAX_LENGTH,
        description="новое имя группы",
    )
