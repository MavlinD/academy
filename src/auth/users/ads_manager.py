from asgiref.sync import sync_to_async
from django.contrib.auth.models import Group
from django.db.models import Q, QuerySet
from logrich.logger_ import errlog, log  # noqa

from src.auth.schemas.ads import AdAttr, AdCreate, AdScheme
from src.auth.schemas.group import GroupCreate
from src.auth.schemas.token import GroupScheme
from src.auth.users.exceptions import GroupNotExists
from src.django_space.ads.models import Ads


class AdManager:
    def __init__(self) -> None:
        self.objects = Ads.objects

    async def create(self, ad_create: AdCreate) -> GroupScheme:
        """Вернуть или создать объявление"""
        ad, _ = await self.objects.aget_or_create(
            name=ad_create.name,
            price=ad_create.price,
            desc=ad_create.desc,
        )
        return await sync_to_async(AdScheme.from_orm)(ad)

    async def update(self, payload) -> Group:
        """update group"""

        await self.objects.filter(Q(name=payload.group) | Q(pk=payload.group)).aupdate(name=payload.new_groupname)
        group: Group = await self.get_one_by_uniq_attr(AdAttr(attr=payload.new_groupname))

        return group

    async def delete(self, group: Group) -> None:
        """remove group"""
        await self.objects.filter(pk=group.pk).adelete()

    async def get_one_by_uniq_attr(self, ad_attr: AdAttr) -> Group | None:
        """get user by uniq user attr"""
        attr = ad_attr.attr
        if isinstance(attr, int) or attr.isdigit():
            ad_in_db = await self.objects.filter(pk=attr).afirst()
        else:
            ad_in_db = await self.objects.filter(name=attr).afirst()
        if not ad_in_db:
            raise GroupNotExists(group=attr)
        return ad_in_db

    async def remove_all_groups(self, user: GroupScheme) -> None:
        """remove user from all groups"""
        ...

    async def get_list_groups(self) -> QuerySet:
        """Вернёт список групп"""
        groups = await sync_to_async(self.objects.all)()
        return groups
