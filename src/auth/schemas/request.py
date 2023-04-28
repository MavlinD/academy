from enum import Enum
from typing import Any, Dict

from fastapi import Body, Query
from pydantic import BaseModel, EmailStr, Field

from src.auth.config import config
from src.auth.schemas.user import secondary_attribute, uniq_attribute


class ActionsType(str, Enum):
    """Перечисление возможных actions в запросе на перемещение в/из группы"""

    add = "add"
    remove = "remove"


class UsersFilter(BaseModel):
    """Модель для фильтрации списка пользователей, исп-ся для валидации параметров запроса"""

    username: uniq_attribute | None
    email: uniq_attribute | None
    is_active: bool | None
    is_superuser: bool | None
    is_staff: bool | None
    first_name: secondary_attribute | None
    last_name: secondary_attribute | None

    search: uniq_attribute | None = Query(
        description="любая часть **\\<username> \\<email> <first_name> <last_name>** пользователя."
        "<br>В **SQLite** регистронезависимый поиск и сопоставление для не **ASCII** символов работать не будет.",
    )
    users: list[int] | None
    groups: list[int] | None


class GroupRename(BaseModel):
    """Схема параметров запроса на переименование группы"""

    group: str | int = Body(
        min_length=1,
        max_length=config.GROUP_MAX_LENGTH,
        description="имя/ID группы для изменения",
    )

    new_groupname: str = Body(
        min_length=config.GROUP_MIN_LENGTH,
        max_length=config.GROUP_MAX_LENGTH,
        description="новое имя группы",
    )


class UserGroupMove(BaseModel):
    """Схема запроса на перемещение пользователя относительно группы"""

    user_attr: str = Field(
        min_length=1,
        max_length=config.USERNAME_ATTR_MAX_LENGTH,
        description="имя/ID пользователя для перемещения",
    )
    group_attr: str = Field(
        min_length=1,
        max_length=config.GROUP_MAX_LENGTH,
        description="имя/ID целевой группы",
    )


class EmailSchema(BaseModel):
    """Схема почтовых отправлений"""

    email: list[EmailStr]
    body: Dict[str, Any]
