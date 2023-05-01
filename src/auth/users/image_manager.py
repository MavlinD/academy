from asgiref.sync import sync_to_async
from django.db.models import Q, QuerySet
from logrich.logger_ import errlog, log  # noqa

from src.auth.schemas.image import ImageCreate, ImageScheme
from src.auth.users.exceptions import GroupNotExists
from src.django_space.ads.models import Ads, Image


class ImageManager:
    def __init__(self) -> None:
        self.objects = Image.objects

    async def create(self, image_create: ImageCreate) -> ImageScheme:
        """Вернуть или создать изображение"""
        image, _ = await self.objects.aget_or_create(path=image_create.path, ads_id=image_create.ads_id)
        return await sync_to_async(ImageScheme.from_orm)(image)

    async def update(self, image: Image, payload: dict) -> Image:
        """update ad"""

        await self.objects.filter(pk=image.pk).aupdate(**payload)
        image: Image = await self.get_one_by_uniq_attr(image_id=image.pk)

        return image

    async def delete(self, ad: Image) -> None:
        """remove ad"""
        await self.objects.filter(pk=ad.pk).adelete()

    async def get_one_by_uniq_attr(self, image_id: int) -> Image | None:
        """get one ad by uniq attr"""
        image_in_db = await self.objects.filter(pk=image_id).afirst()
        if not image_in_db:
            raise GroupNotExists(group=image_id)
        return image_in_db

    async def get_list_ads(self, ad: Ads) -> QuerySet:
        """Вернёт список изображений прикрепленных к одному объявлению."""
        # ads = await sync_to_async(self.objects.all)()
        images = self.objects.filter(ads_id=ad.pk)
        log.debug(images)
        return images
