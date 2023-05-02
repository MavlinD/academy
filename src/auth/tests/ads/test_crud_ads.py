from decimal import Decimal
from typing import Callable

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs
from src.auth.tests.app.test_tools import create_image
from src.django_space.ads.config import config

skip = False
# skip = True
reason = "Temporary off"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_read_ad(client: AsyncClient, routes: Routs, add_test_ad: Callable, add_test_image: Callable) -> None:
    """Тест получения объявления"""
    await create_image(path="картинко.jpg", ads_id=1)
    resp = await client.get(
        routes.request_read_ad(ad_attr=1),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("запрос тестового объявления по ID", o=data)
    assert resp.status_code == 200
    assert Decimal(data.get("price")).quantize(Decimal("1.00")) == Decimal(config.TEST_AD_PRICE)
    assert len(data.get("image_set")) == 2
    await create_image(path="картинко.jpg", ads_id=1)
    resp = await client.get(
        routes.request_read_ad(ad_attr=1),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("попытка добавить второе изображение с тем же именем и тому же объявлению", o=data)
    assert len(data.get("image_set")) == 2


@pytest.mark.skipif(skip, reason=reason)
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


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_update_ad(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    """Тест обновления объявления"""
    name_ad = config.TEST_AD_NAME
    data = {"name": name_ad, "price": 123, "desc": f"desc of ad {name_ad}"}
    resp = await client.patch(
        routes.request_to_update_ad(1),
        json=data,
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание объявления", o=data)
    assert resp.status_code == 200


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_list_ads(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    """Тест списка объявлений"""
    name_ad = "второе тестовое объявление"
    data = {"name": name_ad, "price": 123, "desc": f"desc of ad {name_ad}"}

    resp = await client.put(
        routes.create_ad,
        json=data,
        headers=user_active_auth_headers,
    )
    assert resp.status_code == 201
    resp = await client.get(routes.read_ads)
    log.debug(resp)
    data = resp.json()
    log.debug("список объявлений", o=data)
    assert resp.status_code == 200
    assert len(data) == 2


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_delete_ad(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    """Тест удаления объявления"""
    name_ad = config.TEST_AD_NAME
    data = {"name": name_ad, "price": 123, "desc": f"desc of ad {name_ad}"}

    resp = await client.put(
        routes.create_ad,
        json=data,
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание объявления", o=data)
    assert resp.status_code == 201

    resp = await client.delete(routes.request_delete_ad(2), headers=user_active_auth_headers)
    assert resp.status_code == 204
    resp = await client.get(routes.read_ads)
    log.debug(resp)
    data = resp.json()
    log.debug("список объявлений", o=data)
    assert resp.status_code == 200
    assert len(data) == 1
