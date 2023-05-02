from asgiref.sync import sync_to_async
from logrich.logger_ import errlog, log  # noqa

from src.auth.schemas.image import ImageScheme
from src.auth.users.exceptions import ImageNotExists
from src.django_space.ads.models import Ads, Image


class ImageManager:
    def __init__(self) -> None:
        self.objects = Image.objects

    async def create(self, payload: dict, ad: Ads) -> ImageScheme:
        """Вернуть или создать изображение"""
        image, _ = await self.objects.aget_or_create(**payload, ads_id=ad)
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
            raise ImageNotExists(image=image_id)
        return image_in_db
