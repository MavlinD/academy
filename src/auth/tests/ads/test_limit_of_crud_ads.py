from decimal import Decimal
from typing import Callable

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs
from src.django_space.ads.config import config

skip = False
# skip = True
reason = "Temporary off!"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_cant_create_ad(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    # тест НЕ возможности создать объявление с длинным именем
    name_ad = "test-ad"
    resp = await client.put(
        routes.create_ad,
        json={"name": name_ad * 30, "price": 123, "desc": f"desc of ad {name_ad}"},
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание объявления", o=data)
    assert resp.status_code == 422


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_cant_create_ad_with_err_price(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    # тест НЕ возможности создать объявление с некорректной ценой
    name_ad = "test-ad"
    resp = await client.put(
        routes.create_ad,
        json={"name": name_ad, "price": "fake price", "desc": f"desc of ad {name_ad}"},
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание объявления", o=data)
    assert resp.status_code == 422


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_cant_create_ad_with_err_price_2(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    # тест НЕ возможности создать объявление с некорректной ценой
    name_ad = "test-ad"
    resp = await client.put(
        routes.create_ad,
        json={"name": name_ad, "price": 123.876687908, "desc": f"desc of ad {name_ad}"},
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание объявления", o=data)
    assert resp.status_code == 422
