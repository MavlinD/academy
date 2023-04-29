from typing import Callable

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.conftest import Routs
from src.auth.helpers.tools import print_endpoints  # noqa

skip = True
# skip = False
reason = "Temporary off"

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_group(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
) -> None:
    """
    Тест запроса на создание группы
    https://docs.sqlalchemy.org/en/14/orm/session_basics.html#querying-2-0-style
    """
    payload = {"name": "Группа редакторов"}
    resp = await client.put(routes.create_group, json=payload, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 201
    assert payload["name"] == data["name"]


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_cant_create_group_twice(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
) -> None:
    """Тест невозможности создать новую группу с одинаковым именем"""
    payload = {"name": "Группа-1"}
    resp = await client.put(routes.create_group, json=payload, headers=superuser_auth_headers)
    data = resp.json()
    id1 = data.get("id")
    log.debug("-", o=data)
    assert resp.status_code == 201
    resp = await client.put(routes.create_group, json=payload, headers=superuser_auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    id2 = data.get("id")
    log.debug("-", o=data)
    assert id1 == id2


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_cant_create_group_with_bad_name(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
) -> None:
    """Тест невозможности создать группу с коротким, длинным или состоящим из одних цифр именем"""
    payload = {"name": "123"}
    resp = await client.put(routes.create_group, json=payload, headers=superuser_auth_headers)
    log.debug("-", o=resp.json())
    assert resp.status_code == 422
    # return
    payload = {"name": "Гр"}
    resp = await client.put(routes.create_group, json=payload, headers=superuser_auth_headers)
    assert resp.status_code == 422
    payload = {"name": "Гр" * 400}
    resp = await client.put(routes.create_group, json=payload, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 422


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_cant_create_group_with_bad_name2(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
) -> None:
    """Тест невозможности создать группу с неправильными символами"""
    payload = {"name": "Группа @#&%"}
    resp = await client.put(routes.create_group, json=payload, headers=superuser_auth_headers)
    assert resp.status_code == 422
    data = resp.json()
    log.debug("-", o=data)
    payload = {"name": "Группа @#&%+++"}
    resp = await client.put(routes.create_group, json=payload, headers=superuser_auth_headers)
    # assert resp.status_code == 422
    data = resp.json()
    log.debug("-", o=data)


# @pytest.mark.skipif(skip, reason=reason)
# @pytest.mark.only
@pytest.mark.asyncio
async def test_cant_create_group(
    client: AsyncClient,
    routes: Routs,
    user_active_auth_headers: Headers,
) -> None:
    """Тест невозможности запроса на создание группы для простого пользователя"""
    resp = await client.put(
        routes.create_group,
        json={"name": "Группа редакторов"},
        headers=user_active_auth_headers,
    )
    assert resp.status_code == 403
    data = resp.json()
    log.debug("", o=data)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_list_groups(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    create_group_fixture: Callable,
) -> None:
    """Тест получения списка групп"""
    resp = await client.get(routes.read_groups, headers=superuser_auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    log.debug("-", o=data)
    assert len(data) == 1


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_read_group(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    create_group_fixture: Callable,
) -> None:
    """Тест получения группы"""
    resp = await client.get(routes.read_groups, headers=superuser_auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    log.debug(data)
    # запрос по id
    resp = await client.get(
        routes.request_read_group(group_attr=data[0]["id"]),
        headers=superuser_auth_headers,
    )
    data_one = resp.json()
    log.debug("", o=data_one)
    assert resp.status_code == 200
    assert data_one["id"] == data[0]["id"]
    log.debug("запрос по id", o=data_one)
    return

    param = config.TEST_GROUP
    # запрос по имени группы
    resp = await client.get(routes.request_read_group(group_attr=param), headers=superuser_auth_headers)
    assert resp.status_code == 200
    data_one = resp.json()
    assert param == data_one["name"]
    log.debug("запрос по имени группы", o=data_one)

    # return
    # запрос несуществующей группы
    resp = await client.get(routes.request_read_group(group_attr="fake group"), headers=superuser_auth_headers)
    assert resp.status_code == 404
    data = resp.json()
    log.debug("запрос несуществующей группы.", o=data)
