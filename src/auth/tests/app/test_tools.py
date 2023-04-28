from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from fastapi import HTTPException
from logrich.logger_ import errlog, log  # noqa
from logrich.logger_assets import console  # noqa
from pydantic import EmailStr

from src.auth.config import config
from src.auth.schemas.token import GroupScheme


async def create_first_user() -> User:
    """create FIRST user"""
    user_model = get_user_model()
    user = user_model.objects.create_user(
        email=str(config.FIRST_USER_EMAIL),
        username=str(config.FIRST_USER_USERNAME),
        password=str(config.FIRST_USER_PASSWORD),
        is_superuser=True,
        is_staff=True,
    )
    user.save()
    return user


async def create_user(
    username: str = config.FIRST_USER_USERNAME,
    email: EmailStr = config.FIRST_USER_EMAIL,
    password: str = config.FIRST_USER_PASSWORD,
    is_superuser: bool = False,
    is_staff: bool = False,
    is_active: bool = True,
    first_name: str = "",
    last_name: str = "",
) -> User:
    """create user"""
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_superuser=is_superuser,
        is_staff=is_staff,
        is_active=is_active,
        first_name=first_name,
        last_name=last_name,
    )
    user.save()
    return user


async def create_group(
    groupname: str = config.TEST_GROUP,
) -> GroupScheme:
    """create group"""
    group = Group.objects.create(
        name=groupname,
    )
    group.save()
    return group


async def move_to_group(user: User, group: Group, action: str) -> Group | HTTPException:
    """программное перемещение в/из групп(у/ы), только для тестов"""
    match action:
        case "add":
            user.groups.add(group)
        case "remove":
            user.groups.remove(group)
