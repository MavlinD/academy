from asgiref.sync import sync_to_async
from fastapi import Depends, Path, status
from fastapi_users.router.common import ErrorModel
from logrich.logger_ import log  # noqa
from pydantic import BaseModel

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
from src.django_space.ads.models import Ads, Image
from src.django_space.django_space.adapters import retrieve_ad, retrieve_image

router = APIRouter()


@router.put(
    "/create",
    response_model=ImageScheme,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
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
    image: ImageCreate,
    image_manager: ImageManager = Depends(get_image_manager),
) -> ImageScheme:
    """Создать или вернуть изображение"""
    log.debug(image)
    resp = await image_manager.create(image_create=image)
    # log.debug(image_name)
    # log.debug(resp)
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


@router.get(
    "/{ad_attr:str}",
    # response_model=list[ImageScheme],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
    },
)
async def read_images(
    ad: Ads = Depends(retrieve_ad),
    image_manager: ImageManager = Depends(get_image_manager),
) -> list:
    # ) -> list[ImageScheme]:
    """Получить список изображений по id объявления"""
    log.debug(ad)
    images = await image_manager.get_list_ads(ad=ad)
    # log.debug(dir(images[0]))
    # log.debug(images[0].ads_id)
    # resp = await get_qset_django(qset=images, model=ImageScheme)
    return list(images)
    resp = await ImageScheme.from_orms(images)
    # log.debug(resp)
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
    await image_manager.delete(image)
