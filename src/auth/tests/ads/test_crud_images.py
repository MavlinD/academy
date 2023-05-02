from decimal import Decimal
from typing import Callable

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa
from starlette import status

from src.auth.conftest import Routs
from src.django_space.ads.config import config

skip = False
# skip = True
reason = "Temporary off!"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_image(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    """Тест создания изображения"""
    path_image = "test-image.png"
    resp = await client.put(
        routes.request_create_image(ad_attr=1),
        json={"path": path_image, "is_main": True},
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание изображения..", o=data)
    assert resp.status_code == 201


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_ad_with_over_limit_images(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    """Тест прикрепления свыше лимита изображений."""
    for image in range(0, config.AD_IMAGE_MAX_AMOUNT + 2):
        path_image = f"test-image-{image}.png"
        resp = await client.put(
            routes.request_create_image(ad_attr=1),
            json={"path": path_image},
            headers=user_active_auth_headers,
        )
        log.debug(resp)
        data = resp.json()
        log.debug("запрос тестового объявления по ID..", o=data)

    resp = await client.get(routes.request_read_ad(ad_attr=1))
    log.debug(resp)
    data = resp.json()
    log.debug("запрос тестового объявления по ID.", o=data)
    assert len(data.get("image_set")) == 3


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_update_image(
    client: AsyncClient,
    routes: Routs,
    user_active_auth_headers: Headers,
    add_test_image: Callable,
) -> None:
    """Тест обновления изображения"""
    name_image = "новое_изображение.png"
    # return
    resp = await client.patch(
        routes.request_update_image(image_attr=1),
        json={"path": name_image, "is_main": True},
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на обновление изображения.", o=data)
    assert resp.status_code == status.HTTP_200_OK
    assert data.get("path") == name_image
    assert data.get("is_main") is True


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_delete_image(
    client: AsyncClient,
    routes: Routs,
    user_active_auth_headers: Headers,
    add_test_image: Callable,
) -> None:
    """Тест удаления изображения"""
    name_image = config.TEST_AD_NAME
    # return
    resp = await client.put(
        routes.request_create_image(ad_attr=1),
        json={"path": name_image},
        headers=user_active_auth_headers,
    )
    log.debug(resp)
    data = resp.json()
    log.debug("ответ на создание изображения", o=data)
    assert resp.status_code == 201
    resp = await client.delete(routes.request_delete_image(image_attr=2), headers=user_active_auth_headers)
    assert resp.status_code == 204
    resp = await client.get(
        routes.request_read_ad(ad_attr=1),
    )
    log.debug(resp)
    data = resp.json()
    log.debug("список объявлений", o=data)
    assert resp.status_code == 200
    # должно остаться только одно изображение
    assert len(data.get("image_set", [])) == 1
