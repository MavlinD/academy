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
async def test_update_group(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    create_group_fixture: Callable,
) -> None:
    """Тест обновления группы"""
    resp = await client.get(routes.read_groups, headers=superuser_auth_headers)
    # log.debug(resp)
    assert resp.status_code == 200
    data = resp.json()
    log.debug(data)
    # return
    payload = {
        "group": data[0].get("id"),
        "new_groupname": "Новое имя группы",
    }
    resp = await client.patch(
        routes.request_to_update_group,
        json=payload,
        headers=superuser_auth_headers,
    )
    data_one = resp.json()
    log.debug("обновление", o=data_one)
    # return
    resp = await client.get(routes.read_groups, headers=superuser_auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    log.debug("проверка обновления", o=data)
    assert data[0]["name"] == payload["new_groupname"]
