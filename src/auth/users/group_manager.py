from django.contrib.auth.models import Group
from django.db.models import Q
from logrich.logger_ import errlog, log  # noqa

from src.auth.schemas.group import GroupAttr, GroupCreate
from src.auth.schemas.token import GroupScheme
from src.auth.users.exceptions import GroupNotExists


class GroupManager:
    def __init__(self) -> None:
        self.group_db = Group.objects

    async def create(self, group_create: GroupCreate) -> GroupScheme:
        """Вернуть или создать группу"""
        group, _ = await self.group_db.aget_or_create(name=group_create.name)
        return GroupScheme.from_orm(group)

    async def update(self, payload) -> GroupScheme:
        """update group"""

        await self.group_db.filter(Q(name=payload.group) | Q(pk=payload.group)).aupdate(name=payload.new_groupname)
        group: Group = await self.get_group_by_uniq_attr(GroupAttr(attr=payload.new_groupname))

        return GroupScheme.from_orm(group)

    async def delete(self, group: GroupScheme) -> None:
        """remove group"""
        await self.group_db.filter(pk=group.id).adelete()

    async def get_group_by_uniq_attr(self, group_attr: GroupAttr) -> Group | None:
        """get user by uniq user attr"""
        attr = group_attr.attr
        if isinstance(attr, int) or attr.isdigit():
            group_in_db = await self.group_db.filter(pk=attr).afirst()
        else:
            group_in_db = await self.group_db.filter(name=attr).afirst()
        if not group_in_db:
            raise GroupNotExists(group=attr)
        return group_in_db

    async def remove_all_groups(self, user: GroupScheme) -> None:
        """remove user from all groups"""
        ...

    async def get_list_groups(self) -> list[GroupScheme]:
        """Вернёт список групп"""
        groups = self.group_db.all()
        return list(groups)
