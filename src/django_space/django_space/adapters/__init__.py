from typing import Type, TypeVar

from django.contrib.auth.models import User
from django.db import models
from fastapi import Depends, HTTPException, Path
from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.schemas.ads import AdAttr
from src.auth.schemas.user import UserAttr
from src.auth.users.ads_manager import AdManager
from src.auth.users.init import get_ads_manager, get_image_manager, get_user_manager
from src.auth.users.user_manager import UserManager
from src.django_space.ads.config import config as ad_config
from src.django_space.ads.models import Ads, Image

ModelT = TypeVar("ModelT", bound=models.Model)


async def retrieve_users(
    user_attr: str = Path(
        min_length=1,
        max_length=config.USERNAME_ATTR_MAX_LENGTH,
        description="username, email, ID пользователя",
    ),
    user_manager: UserManager = Depends(get_user_manager),
) -> User:
    """получить пользователя"""
    attr = UserAttr(attr=user_attr)
    # log.trace(attr)
    user: User = await user_manager.get_user_by_uniq_attr(user_attr=attr)
    # log.debug(user)
    return user


async def retrieve_ad(
    ad_attr: int = Path(
        description="ID объявления",
    ),
    ads_manager: AdManager = Depends(get_ads_manager),
) -> Ads:
    """получить объявление"""
    attr = AdAttr(attr=ad_attr)
    # log.trace(attr)
    ad: Ads = await ads_manager.get_one_by_uniq_attr(ad_attr=attr)
    # log.debug(user)
    return ad


async def retrieve_image(
    image_id: int = Path(
        description="ID изображения",
    ),
    images_manager: AdManager = Depends(get_image_manager),
) -> Image:
    """получить изображение"""
    # attr = AdAttr(attr=image_attr)
    # log.trace(attr)
    image: Image = await images_manager.get_one_by_uniq_attr(image_id=image_id)
    # log.debug(user)
    return image
