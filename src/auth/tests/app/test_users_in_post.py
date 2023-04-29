# type: ignore

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs
from src.auth.schemas.request import ActionsType
from src.auth.schemas.token import UserScheme
from src.auth.tests.app.test_tools import create_group, create_user, move_to_group

# skip = False
skip = True
reason = "Temporary off!!"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_list_users_post(
    client: AsyncClient,
    routes: Routs,
    regular_user: UserScheme,
    superuser_auth_headers: Headers,
) -> None:
    """Тест фильтра пользователей по списку ID групп"""

    users = []
    groups = []

    user = await create_user(
        username="tony",
        password="Pass^712",
        email="zoo@tst.ml",
        first_name="Федор",
        last_name="Букряев",
    )
    assert hasattr(user, "id")
    if hasattr(user, "id"):
        users.append(str(getattr(user, "id")))
    group = await create_group("первая группа")
    # return
    groups.append(
        str(
            getattr(group, "id"),
        )
    )
    # log.debug(type(user))
    # return
    # assert isinstance(user, UserOutSUWithGroups)
    # assert isinstance(group, GroupScheme)
    await move_to_group(user=user, group=group, action=ActionsType.add)
    # return

    user = await create_user(
        username="bazoo",
        password="Pass^712",
        email="costa@tst.ml",
        first_name="Анатолий",
        last_name="Букреев",
    )
    # assert isinstance(user, UserOutSUWithGroups)
    # return
    users.append(str(getattr(user, "id")))
    group = await create_group("вторая группа")
    # assert isinstance(group, GroupScheme)
    groups.append(str(group.id))
    await move_to_group(user=user, group=group, action=ActionsType.add)
    # return

    user = await create_user(
        username="serg",
        password="Pass^712",
        email="bravo@mail.ml",
        first_name="Юрий",
        last_name="Шатунов",
        is_active=True,
        is_staff=True,
    )
    # assert isinstance(user, UserOutSUWithGroups)
    users.append(str(user.id))
    await move_to_group(user=user, group=group, action=ActionsType.add)
    # --------------------------------
    params = {
        "payload": {
            # "users": users[:-1],
            "users": users,
            # "groups": groups,
            "groups": groups[1:],  # нужны только те, что в последней группе
        },
        "paginate": {"page": 1, "size": 10},
    }
    resp = await client.post(routes.list_of_users_post, json=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("only users in list groups", o=data)
    assert len(data.get("items")) == 2
    # return

    # --------------------------------
    params = {
        "payload": {
            "is_staff": True,
            "users": users,
            "groups": groups[1:],  # нужны только те, что в последней группе
        },
        "paginate": {"page": 1, "size": 10},
    }
    resp = await client.post(routes.list_of_users_post, json=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("only users in list groups", o=data)
    # return
    assert len(data.get("items")) == 1
    assert data.get("items")[0].get("username") == user.username
