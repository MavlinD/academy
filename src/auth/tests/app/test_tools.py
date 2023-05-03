import decimal

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from logrich.logger_ import errlog, log  # noqa
from logrich.logger_assets import console  # noqa
from pydantic import EmailStr

from src.auth.config import config
from src.django_space.ads.config import config as ad_config
from src.django_space.ads.models import Ads, Image


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
    user = await sync_to_async(user_model.objects.create_user)(
        username=username,
        email=email,
        password=password,
        is_superuser=is_superuser,
        is_staff=is_staff,
        is_active=is_active,
        first_name=first_name,
        last_name=last_name,
    )
    return user


async def create_ad(
    name: str = ad_config.TEST_AD_NAME,
    price: decimal = ad_config.TEST_AD_PRICE,
    desc: str = ad_config.TEST_AD_DESC,
) -> Ads:
    """create ad"""
    ad_model = Ads
    ad = await sync_to_async(ad_model.objects.get_or_create)(
        name=name,
        price=price,
        desc=desc,
    )
    return ad


async def create_image(path: str = ad_config.TEST_IMAGE_PATH, ads_id: int = 1, is_main: bool = False) -> Image:
    """create ad"""
    ad = await Ads.objects.filter(pk=ads_id).afirst()
    image_model = Image
    image = await sync_to_async(image_model.objects.get_or_create)(path=path, ads_id=ad, is_main=is_main)
    return image
