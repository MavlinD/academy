from decimal import Decimal
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


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_read_ad(client: AsyncClient, routes: Routs, add_test_ad: Callable) -> None:
    """Тест получения объявления"""
    resp = await client.get(
        routes.request_read_ad(ad_attr=config.TEST_AD_NAME),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("запрос тестового объявления по имени", o=data)
    assert resp.status_code == 200
    assert Decimal(data.get("price")).quantize(Decimal("1.00")) == Decimal(config.TEST_AD_PRICE)
    resp = await client.get(
        routes.request_read_ad(ad_attr=1),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("запрос тестового объявления по ID", o=data)
    assert resp.status_code == 200
    assert Decimal(data.get("price")).quantize(Decimal("1.00")) == Decimal(config.TEST_AD_PRICE)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_ad(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
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
    assert data.get("id") == 2


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_update_ad(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    """Тест обновления объявления"""
    name_ad = config.TEST_AD_NAME
    data = {"name": name_ad, "price": 123, "desc": f"desc of ad {name_ad}"}
    resp = await client.patch(
        routes.request_to_update_ad(name_ad),
        json=data,
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание объявления", o=data)
    assert resp.status_code == 200
