from decimal import Decimal
from typing import Callable

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs
from src.django_space.ads.config import config

# skip = False
skip = True
reason = "Temporary off!"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_image(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    """Тест создания изображения"""
    path_image = "test-image.png"
    resp = await client.put(
        routes.create_image,
        json={
            "path": path_image,
            "ads_id": 1,
        },
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание изображения", o=data)
    assert resp.status_code == 201
    # return
    path_image = "test-image2.png"
    resp = await client.put(
        routes.create_image,
        json={
            "path": path_image,
            "ads_id": 1,
        },
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание второго изображения", o=data)
    assert resp.status_code == 201


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_read_image(client: AsyncClient, routes: Routs, add_test_ad: Callable, add_test_image: Callable) -> None:
    """Тест получения изображения"""
    resp = await client.get(
        routes.request_read_image(ad_attr=1),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("запрос тестового изображения по ID", o=data)
    assert resp.status_code == 200
    assert Decimal(data.get("price")).quantize(Decimal("1.00")) == Decimal(config.TEST_AD_PRICE)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_update_image(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_image: Callable
) -> None:
    """Тест обновления изображения"""
    name_image = config.TEST_AD_NAME
    data = {"name": name_image, "price": 123, "desc": f"desc of ad {name_image}"}
    resp = await client.patch(
        routes.request_to_update_image(1),
        json=data,
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание изображения", o=data)
    assert resp.status_code == 200


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_list_images(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_image: Callable
) -> None:
    """Тест списка объявлений"""
    name_image = "второе тестовое объявление"
    data = {"name": name_image, "price": 123, "desc": f"desc of ad {name_image}"}

    resp = await client.put(
        routes.create_image,
        json=data,
        headers=user_active_auth_headers,
    )
    # log.debug(resp)
    # data = resp.json()
    # log.debug("ответ на создание изображения", o=data)
    assert resp.status_code == 201
    resp = await client.get(routes.read_images)
    log.debug(resp)
    data = resp.json()
    log.debug("список объявлений", o=data)
    assert resp.status_code == 200
    assert len(data) == 2


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_delete_image(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_image: Callable
) -> None:
    """Тест удаления изображения"""
    name_image = config.TEST_AD_NAME
    data = {"name": name_image, "price": 123, "desc": f"desc of ad {name_image}"}

    resp = await client.put(
        routes.create_image,
        json=data,
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание изображения", o=data)
    assert resp.status_code == 201

    resp = await client.delete(routes.request_delete_image(2), headers=user_active_auth_headers)
    assert resp.status_code == 204
    resp = await client.get(routes.read_images)
    log.debug(resp)
    data = resp.json()
    log.debug("список объявлений", o=data)
    assert resp.status_code == 200
    assert len(data) == 1
