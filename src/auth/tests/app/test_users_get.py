# type: ignore
import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs
from src.auth.helpers.tools import check_resp
from src.auth.schemas.token import UserScheme
from src.auth.tests.app.conftest import insert_fake_data_to_db
from src.auth.tests.app.test_tools import create_user

skip = False
# skip = True
reason = "Temporary off!"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_list_users_get(
    client: AsyncClient,
    routes: Routs,
    regular_user: UserScheme,
    superuser_auth_headers: Headers,
) -> None:
    """Тест списка пользователей с пагинацией"""
    AMOUNT_USERS = 10
    SIZE = 5
    PAGE = 1

    await insert_fake_data_to_db(amount_users=AMOUNT_USERS)

    params = {"page": str(PAGE), "size": str(SIZE)}

    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("first page-", o=data)
    # return
    assert data.get("total") == 2 + AMOUNT_USERS
    assert len(data.get("items")) == SIZE
    assert data.get("page") == PAGE
    assert data.get("size") == SIZE

    PAGE = 3
    params = {"page": str(PAGE), "size": str(SIZE)}

    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    # log.debug("last page", o=data)
    # return
    assert data.get("total") == 2 + AMOUNT_USERS
    assert len(data.get("items")) == 2 + AMOUNT_USERS - SIZE * (PAGE - 1)
    assert data.get("page") == PAGE
    assert data.get("size") == SIZE


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_list_users_v2_get_paginate(
    client: AsyncClient,
    routes: Routs,
    regular_user: UserScheme,
    superuser_auth_headers: Headers,
) -> None:
    """Тест списка пользователей"""

    users = set()

    user = await create_user(
        username="tony",
        password="Pass^712",
        email="zoO@tst.ml",
        first_name="Федор",
        last_name="Букряев",
    )
    assert hasattr(user, "id")
    if hasattr(user, "id"):
        users.add(str(getattr(user, "id")))
    user = await create_user(
        username="bazoo",
        password="Pass^712",
        email="costa@tst.Ml",
        first_name="Анатолий",
        last_name="Букреев",
    )
    assert hasattr(user, "id")
    if hasattr(user, "id"):
        users.add(str(getattr(user, "id")))
    user = await create_user(
        username="serg",
        password="Pass^712",
        email="bravo@mail.ml",
        first_name="Юрий",
        last_name="Шатунов",
        is_staff=True,
    )
    assert hasattr(user, "id")
    if hasattr(user, "id"):
        users.add(str(getattr(user, "id")))

    params = {"search": "Семё"}
    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("filter users", o=params)
    log.trace("", o=data)
    # return
    assert len(data.get("items")) == 1
    # --------------------------------
    params = {"search": "tst"}
    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("filter users", o=params)
    assert len(data.get("items")) == 2
    # --------------------------------
    params = {"search": "t.ml"}
    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("filter users", o=params)
    assert len(data.get("items")) == 2
    # --------------------------------
    params = {"search": "кряев"}
    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("filter users", o=params)
    # log.debug('', o=data)
    assert len(data.get("items")) == 1
    # --------------------------------
    params = {"search": "Бук"}
    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("filter users", o=params)
    assert len(data.get("items")) == 2
    # --------------------------------
    params = {"search": "бук"}
    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("filter users", o=params)
    # log.debug("", o=data)
    assert len(data.get("items")) == 2
    # --------------------------------
    params = {"is_staff": "yes"}
    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("only staff", o=data)
    assert len(data.get("items")) == 2
    # --------------------------------
    params = {"is_staff": "no"}
    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("only NO staff", o=data)
    assert len(data.get("items")) == 3
    # --------------------------------
    params = {"is_staff": "no", "search": "Бук"}
    resp = await client.get(routes.list_of_users_get, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("only NO staff and 'Бук'", o=data)
    # return
    assert len(data.get("items")) == 2
    # --------------------------------
    resp = await client.get(routes.list_of_users_get, params={}, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("without params return all user in paginate", o=data)
    assert len(data.get("items")) == 5
    # log.debug(users)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_can_not_list_users_for_nonsuper_user(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers
) -> None:
    """Тест отказа в списке пользователей обычному пользователю"""
    resp = await client.get(routes.list_of_users, headers=user_active_auth_headers)
    check_resp(resp, 403)
