from __future__ import annotations

from fastapi import Body, Path
from logrich.logger_ import log  # noqa
from pydantic import BaseModel

from src.auth.config import config

# regex_create = r"^[a-z]+[a-z0-9-]*$(?i)"
# форма записи указанная выше также работает, но выводит НЕ корретный ответ -
# подсказку каким регекспом обрабатывается запрос и inline flag для юникода в python не реализован
# такая форма записи выводит корретный ответ
regex_create = r"^[A-Za-zа-яА-Я]+[A-Za-zа-яА-Я0-9-\s]*$"
# два регеэкспа тк запрос может быть выполнен по ID группы
regex_read = r"^[A-Za-zа-яА-Я0-9-\s]*$"


constrain_group = Body(
    min_length=config.GROUP_MIN_LENGTH,
    max_length=config.GROUP_MAX_LENGTH,
    description="Имя группы",
    regex=regex_create,
)

constrain_group_path = Path(
    min_length=1,
    max_length=config.GROUP_MAX_LENGTH,
    description="Имя или ID группы",
    regex=regex_read,
)


class GroupCreate(BaseModel):
    """Схема для создания группы"""

    name: str = constrain_group


class GroupAttr(BaseModel):
    """Схема для валидации параметров внутри приложения"""

    attr: str | int = constrain_group_path


class GroupOut(BaseModel):
    """Схема для вывода групп в разрезе пользователей"""

    name: str
    id: str

    class Config:
        orm_mode = True
