from typing import Any, Callable, Type, TypeVar

from django.contrib.auth.models import User
from django.db import models
from fastapi import Body, Depends, HTTPException, Path
from logrich.logger_ import log  # noqa
from pydantic import Field
from starlette.requests import Request

from src.auth.config import config
from src.auth.schemas.ads import AdAttr
from src.auth.schemas.image import ImageCreate, ImageScheme
from src.auth.schemas.scheme_tools import get_qset
from src.auth.schemas.user import UserAttr
from src.auth.users.ads_manager import AdManager
from src.auth.users.image_manager import ImageManager
from src.auth.users.init import get_ads_manager, get_image_manager, get_user_manager
from src.auth.users.user_manager import UserManager
from src.django_space.ads.config import config as ad_config
from src.django_space.ads.exception import OverLimitAmountImages
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


class ImageAmountChecker:
    def __init__(self, image_max_amount: int = ad_config.AD_IMAGE_MAX_AMOUNT) -> None:
        """проверить ограничение на максимальное кол-во прикрепленных изображений"""
        self.image_max_amount = image_max_amount

    async def __call__(self, ad: Ads = Depends(retrieve_ad)) -> Any:
        amount_images = await get_qset(qset=ad.image_set, model=ImageScheme)
        aim = list(amount_images)
        # log.debug(aim)
        if len(aim) >= self.image_max_amount:
            raise OverLimitAmountImages(ad=ad)


async def retrieve_image(
    image_attr: int = Path(
        description="ID изображения",
    ),
    images_manager: ImageManager = Depends(get_image_manager),
) -> Image:
    """получить изображение"""

    image: Image = await images_manager.get_one_by_uniq_attr(image_id=image_attr)
    return image
