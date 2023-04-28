from typing import Callable

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)

skip = False
# skip = True
reason = "Temporary off!"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.parametrize("attr,resp_code,resp_len", [("id", 204, 0)])
@pytest.mark.asyncio
async def test_delete_group_by_id(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    create_group_fixture: Callable,
    attr: str,
    resp_code: int,
    resp_len: int,
) -> None:
    """Тест удаления группы по ID"""
    await delete_group(client, routes, superuser_auth_headers, attr, resp_code, resp_len)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.parametrize("attr,resp_code,resp_len", [("name", 204, 0)])
@pytest.mark.asyncio
async def test_delete_group_by_name(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    create_group_fixture: Callable,
    attr: str,
    resp_code: int,
    resp_len: int,
) -> None:
    """Тест удаления группы по имени"""
    await delete_group(client, routes, superuser_auth_headers, attr, resp_code, resp_len)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.parametrize("attr,resp_code,resp_len", [("fake_attr", 404, 1)])
@pytest.mark.asyncio
async def test_delete_unexist_group(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    create_group_fixture: Callable,
    attr: str,
    resp_code: int,
    resp_len: int,
) -> None:
    """Тест удаления группы по имени"""
    await delete_group(client, routes, superuser_auth_headers, attr, resp_code, resp_len)


async def delete_group(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    attr: str,
    resp_code: int,
    resp_len: int,
) -> None:
    """Тест удаления группы"""
    resp = await client.get(routes.read_groups, headers=superuser_auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    log.debug("проверка наличия группы", o=data)

    resp = await client.delete(
        routes.request_delete_group(group_attr=data[0].get(attr)),
        headers=superuser_auth_headers,
    )
    log.debug(f"удаление по {attr}", o=resp)
    assert resp.status_code == resp_code
    resp = await client.get(routes.read_groups, headers=superuser_auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    log.debug("проверка удаления", o=data)
    assert len(data) == resp_len
