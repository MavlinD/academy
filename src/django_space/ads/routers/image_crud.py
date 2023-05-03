from fastapi import Depends, status
from logrich.logger_ import log  # noqa

from src.auth.assets import APIRouter
from src.auth.schemas.image import ImageCreate, ImageScheme
from src.auth.users.dependencies import get_current_active_user
from src.auth.users.image_manager import ImageManager
from src.auth.users.init import get_image_manager
from src.django_space.ads.config import config
from src.django_space.ads.models import Ads, Image
from src.django_space.django_space.adapters import (
    ImageLimitChecker,
    retrieve_ad,
    retrieve_image,
)
from src.django_space.django_space.routers.jwt_obtain import unauthorized_responses

router = APIRouter()


@router.put(
    "/{ad_attr:str}",
    response_model=ImageScheme,
    description=f"К объявлению можно прикрепить до **{config.AD_IMAGE_MAX_AMOUNT}** изображений включительно.<br>"
    f"И назначить до **{config.AD_IMAGE_MAIN_MAX_AMOUNT}** изображений(я) главными.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_active_user),
        Depends(ImageLimitChecker()),
    ],
    responses={
        **unauthorized_responses,
    },
)
async def create_image(
    payload: ImageCreate,
    ad: Ads = Depends(retrieve_ad),
    image_manager: ImageManager = Depends(get_image_manager),
) -> ImageScheme:
    """Создать (прикрепить) изображение."""
    resp = await image_manager.create(payload=payload.dict(exclude_unset=True, exclude_none=True), ad=ad)
    return resp


@router.patch(
    "/{image_attr:str}",
    response_model=ImageScheme,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_user)],
    responses={
        **unauthorized_responses,
    },
)
async def update_image(
    payload: ImageCreate,
    image: Image = Depends(retrieve_image),
    image_manager: ImageManager = Depends(get_image_manager),
) -> ImageScheme:
    """Обновить изображение по имени или id."""
    image = await image_manager.update(image=image, payload=payload.dict(exclude_unset=True, exclude_none=True))
    resp = await ImageScheme.from_orms(image)
    return resp


@router.delete(
    "/{image_attr:str}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_user)],
    responses={
        **unauthorized_responses,
        status.HTTP_404_NOT_FOUND: {
            "description": "The image does not exist.",
        },
    },
)
async def delete_image(
    image: Image = Depends(retrieve_image),
    image_manager: ImageManager = Depends(get_image_manager),
) -> None:
    """Удалить изображение по id."""
    await image_manager.delete(image)
