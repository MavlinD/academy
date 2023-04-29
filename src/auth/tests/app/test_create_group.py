from typing import Callable

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs

skip = False
# skip = True
reason = "Temporary off"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_list_groups(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    create_group_fixture: Callable,
) -> None:
    """Тест создания группы"""
    resp = await client.put(
        routes.create_group,
        json={"name": "test-group"},
        headers=superuser_auth_headers,
    )
    assert resp.status_code == 201
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание группы", o=data)
    resp = await client.get(routes.read_groups, headers=superuser_auth_headers)
    log.debug(resp)
    # return
    data = resp.json()
    log.debug("--", o=data)
    # assert len(data) == 2
    # assert resp.status_code == 200


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_group(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    create_group_fixture: Callable,
) -> None:
    """Тест списка групп"""
    resp = await client.put(
        routes.create_group,
        json={"name": "test-group"},
        headers=superuser_auth_headers,
    )
    # log.debug(resp)
    data = resp.json()
    log.debug("--", o=data)
    assert resp.status_code == 201
    resp = await client.get(routes.read_groups, headers=superuser_auth_headers)
    log.debug(resp)
    # return
    data = resp.json()
    log.debug("--", o=data)
