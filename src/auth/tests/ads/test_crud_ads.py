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
async def test_create_ad(
    client: AsyncClient,
    routes: Routs,
    user_active_auth_headers: Headers,
) -> None:
    """Тест создания объявления"""
    name_ad = "test-ad"
    resp = await client.put(
        routes.create_ad,
        json={"name": name_ad, "price": 123, "desc": f"desc of ad {name_ad}"},
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание объявления", o=data)
    assert resp.status_code == 201
