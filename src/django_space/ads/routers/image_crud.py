from asgiref.sync import sync_to_async
from fastapi import Body, Depends, Path, status
from fastapi_users.router.common import ErrorModel
from logrich.logger_ import log  # noqa
from pydantic import BaseModel
from pydantic.typing import Annotated

from src.auth.assets import APIRouter
from src.auth.handlers.errors.codes import ErrorCodeLocal
from src.auth.schemas.ads import AdAttr, AdCreate, AdScheme
from src.auth.schemas.image import ImageCreate, ImageScheme
from src.auth.schemas.scheme_tools import get_qset, get_qset_django
from src.auth.users.ads_manager import AdManager
from src.auth.users.dependencies import get_current_active_user
from src.auth.users.image_manager import ImageManager
from src.auth.users.init import get_ads_manager, get_image_manager
from src.django_space.ads.config import config
from src.django_space.ads.config import config as ad_config
from src.django_space.ads.exception import OverLimitAmountImages
from src.django_space.ads.models import Ads, Image
from src.django_space.django_space.adapters import (
    ImageAmountChecker,
    retrieve_ad,
    retrieve_image,
)

router = APIRouter()


@router.put(
    "/{ad_attr:str}",
    response_model=ImageScheme,
    description=f"К объявлению можно прикрепить до **{config.AD_IMAGE_MAX_AMOUNT}** изображений включительно.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_active_user),
        Depends(ImageAmountChecker()),
    ],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCodeLocal.GROUP_ALREADY_EXISTS: {
                            "summary": "A group with this name already exists.",
                            "value": {"detail": ErrorCodeLocal.GROUP_ALREADY_EXISTS},
                        },
                    }
                }
            },
        },
    },
)
async def create_image(
    payload: ImageCreate,
    ad: Ads = Depends(retrieve_ad),
    image_manager: ImageManager = Depends(get_image_manager),
) -> ImageScheme:
    """Создать изображение"""
    resp = await image_manager.create(payload=payload.dict(exclude_unset=True, exclude_none=True), ad=ad)
    return resp


@router.patch(
    "/{image_attr:str}",
    response_model=ImageScheme,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_user)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
    },
)
async def update_image(
    payload: ImageCreate,
    image: Image = Depends(retrieve_image),
    image_manager: ImageManager = Depends(get_image_manager),
) -> ImageScheme:
    """Обновить изображение по имени или id"""
    image = await image_manager.update(image=image, payload=payload.dict(exclude_unset=True, exclude_none=True))
    resp = await ImageScheme.from_orms(image)
    return resp


@router.delete(
    "/{image_attr:str}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_user)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The image does not exist.",
        },
    },
)
async def delete_image(
    image: Image = Depends(retrieve_image),
    image_manager: ImageManager = Depends(get_image_manager),
) -> None:
    """Удалить изображение по id"""
    # log.debug(image)
    await image_manager.delete(image)
