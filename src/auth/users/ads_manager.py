from asgiref.sync import sync_to_async
from django.db.models import QuerySet
from logrich.logger_ import errlog, log  # noqa

from src.auth.schemas.ads import AdAttr, AdCreate, AdScheme
from src.auth.users.exceptions import AdNotExists, GroupNotExists
from src.django_space.ads.models import Ads


class AdManager:
    def __init__(self) -> None:
        self.objects = Ads.objects

    async def create(self, ad_create: AdCreate) -> AdScheme:
        """Вернуть или создать объявление"""
        ad, _ = await self.objects.aget_or_create(
            name=ad_create.name,
            price=ad_create.price,
            desc=ad_create.desc,
        )
        return await sync_to_async(AdScheme.from_orm)(ad)

    async def update(self, ad: Ads, payload: dict) -> Ads:
        """update ad"""

        await self.objects.filter(pk=ad.pk).aupdate(**payload)
        ad: Ads = await self.get_one_by_uniq_attr(AdAttr(attr=ad.pk))

        return ad

    async def delete(self, ad: Ads) -> None:
        """remove ad"""
        await self.objects.filter(pk=ad.pk).adelete()

    async def get_one_by_uniq_attr(self, ad_attr: AdAttr) -> Ads | None:
        """get one ad by uniq attr"""
        attr = ad_attr.attr
        if isinstance(attr, int) or attr.isdigit():
            ad_in_db = await self.objects.filter(pk=attr).afirst()
        else:
            ad_in_db = await self.objects.filter(name=attr).afirst()
        if not ad_in_db:
            raise AdNotExists(ad=attr)
        return ad_in_db

    async def get_list_ads(self) -> QuerySet:
        """Вернёт список объявлений"""
        ads = await sync_to_async(self.objects.all)()
        return ads
