from typing import Any

from fastapi import Depends, Path, Request
from fastapi_pagination import Page
from logrich.logger_ import log  # noqa
from pydantic import Field

from src.auth.schemas.ads import AdAttr
from src.auth.schemas.image import ImageScheme
from src.auth.schemas.scheme_tools import get_qset
from src.auth.users.ads_manager import AdManager
from src.auth.users.image_manager import ImageManager
from src.auth.users.init import get_ads_manager, get_image_manager
from src.django_space.ads.config import config as ad_config
from src.django_space.ads.exception import OverLimitAmountImages, OverLimitMainImages
from src.django_space.ads.models import Ads, Image


async def retrieve_ad(
    ad_attr: int = Path(
        description="ID объявления",
    ),
    ads_manager: AdManager = Depends(get_ads_manager),
) -> Ads:
    """получить объявление"""
    attr = AdAttr(attr=ad_attr)
    ad: Ads = await ads_manager.get_one_by_uniq_attr(ad_attr=attr)
    return ad


class ImageLimitChecker:
    def __init__(
        self,
        image_max_amount: int = ad_config.AD_IMAGE_MAX_AMOUNT,
        image_main_max_amount: int = ad_config.AD_IMAGE_MAIN_MAX_AMOUNT,
    ) -> None:
        """
        проверить ограничение:
        - на максимальное кол-во прикрепленных изображений
        - на максимальное кол-во главных изображений
        """
        self.image_max_amount = image_max_amount
        self.image_main_max_amount = image_main_max_amount

    async def __call__(self, request: Request, ad: Ads = Depends(retrieve_ad)) -> Any:
        amount_images = await get_qset(qset=ad.image_set, model=ImageScheme)
        all_images = list(amount_images)
        is_main = [image for image in all_images if image.is_main]
        req = await request.json()
        if req.get("is_main") and len(is_main) >= self.image_main_max_amount:
            raise OverLimitMainImages(ad=ad)
        if len(all_images) >= self.image_max_amount:
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


# параметры пагинации по умолчанию
Page = Page.with_custom_options(
    size=Field(10, ge=1, le=15),
)
