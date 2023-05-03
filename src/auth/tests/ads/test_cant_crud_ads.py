from typing import Callable

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs
from src.django_space.ads.config import config

skip = False
# skip = True
reason = "Temporary off"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_ad(client: AsyncClient, routes: Routs, user_active_auth_headers: Headers) -> None:
    """Тест НЕ создания объявления"""
    name_ad = "test-ad"
    resp = await client.put(
        routes.create_ad,
        json={"name": name_ad, "price": 123.55555, "desc": f"desc of ad {name_ad}"},
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание объявления.", o=data)
    assert resp.status_code == 422

    resp = await client.put(
        routes.create_ad,
        json={"name": name_ad, "price": 1235253634634634.55, "desc": f"desc of ad {name_ad}"},
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание объявления.", o=data)
    assert resp.status_code == 422


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_update_ad(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    """Тест НЕ обновления объявления"""
    name_ad = config.TEST_AD_NAME
    data = {"name": name_ad, "price": 123.979, "desc": f"desc of ad {name_ad}"}
    resp = await client.patch(
        routes.request_to_update_ad(1),
        json=data,
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на обновление объявления", o=data)
    assert resp.status_code == 422
    data = {"name": name_ad, "price": 1233453645326.79, "desc": f"desc of ad {name_ad}"}
    resp = await client.patch(
        routes.request_to_update_ad(1),
        json=data,
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на обновление объявления", o=data)
    assert resp.status_code == 422
