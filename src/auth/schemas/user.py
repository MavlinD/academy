from string import Template
from typing import Annotated, TypeAlias

from logrich.logger_ import log  # noqa
from pydantic import BaseModel, EmailStr, Field

description_username_attr = "username - Уникальный атрибут пользователя"
description_uniq_attr = "Уникальный атрибут пользователя"
uniq_attribute: TypeAlias = Annotated[
    str | int | EmailStr, Field(min_length=1, max_length=150, description=description_uniq_attr)
]

limit_of_username: TypeAlias = Annotated[
    str, Field(min_length=3, max_length=150, description=description_username_attr)
]


secondary_attribute: TypeAlias = Annotated[str, Field(max_length=64)]

PASS_MIN_LEN = 6  # минимальная длина пароля
PASS_MAX_LEN = 18  # максимальная длина пароля
regex = Template(
    "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$$!%*^#+?&])[A-Za-z\d@$$!^#+%*?&]{$minlen,$maxlen}$$"  # noqa
).substitute(
    minlen=PASS_MIN_LEN, maxlen=PASS_MAX_LEN
)  # noqa
# https://stackabuse.com/formatting-strings-with-the-python-template-class/
password_description = (
    f"Please enter password should be: "
    f"(Минимум одна заглавная буква, минимум один спец.символ, минимум одна цифра)"
    f" и длина должна быть от {PASS_MIN_LEN} до {PASS_MAX_LEN}"
)
limit_of_password: TypeAlias = Annotated[str, Field(regex=regex, description=password_description)]


class UserCreate(BaseModel):
    """Схема создания пользователя"""

    username: limit_of_username
    email: EmailStr
    password: limit_of_password
    is_active: bool = True
    is_superuser: bool = False
    is_staff: bool = False
    first_name: secondary_attribute = ""
    last_name: secondary_attribute = ""


class UserUpdate(BaseModel):
    """Схема для запроса на обновление"""

    username: uniq_attribute | None
    email: EmailStr | None
    first_name: secondary_attribute | None
    last_name: secondary_attribute | None
    is_superuser: bool | None
    is_staff: bool | None
    is_active: bool | None


class PasswordReset(BaseModel):
    """Запрос на обновление пароля"""

    token: str = Field(max_length=3000)
    password: limit_of_password


class UserAttr(BaseModel):
    """Схема для валидации параметров запроса на получение пользователя"""

    attr: uniq_attribute
