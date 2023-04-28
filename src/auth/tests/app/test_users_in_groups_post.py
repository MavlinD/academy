# type: ignore
import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs
from src.auth.schemas.token import UserScheme
from src.auth.tests.app.test_tools import create_user

skip = False
# skip = True
reason = "Temporary off!"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_list_users_in_gr(
    client: AsyncClient,
    routes: Routs,
    regular_user: UserScheme,
    superuser_auth_headers: Headers,
) -> None:
    """Тест фильтра пользователей по списку ID пользователей"""
    users = []

    user = await create_user(
        username="tony",
        password="Pass^712",
        email="zoo@tst.ml",
        first_name="юрий",
        last_name="Букряев",
    )

    user = await create_user(
        username="bazoo",
        password="Pass^712",
        email="costa@tst.ml",
        first_name="Анатолий",
        last_name="smit",
    )
    users.append(str(getattr(user, "id")))
    user = await create_user(
        username="serg",
        password="Pass^712",
        email="bravo@mail.ml",
        first_name="Юрий",
        last_name="Smit",
        is_active=True,
    )
    users.append(str(getattr(user, "id")))

    # --------------------------------
    params = {"search": "юрий"}
    # для не ASCII символов в sqlite поиск и сопоставление не работают
    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("filter users", o=params)
    assert len(data.get("items")) == 2
    # --------------------------------
    params = {"search": "smit"}
    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("filter users", o=params)
    assert len(data.get("items")) == 2
    # --------------------------------
    params2 = {
        "payload": {
            "users": users,
        },
        "paginate": {"page": 1, "size": 10},
    }
    resp = await client.post(routes.list_of_users_post, json=params2, headers=superuser_auth_headers)
    data = resp.json()
    log.trace("", o=users)
    log.debug("only users in group", o=data)
    items = data.get("items")
    uids = []
    assert len(items) == 2
    for u in items:
        uids.append(u.get("id"))
    assert int(users[0]) in uids
