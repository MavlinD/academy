from typing import Callable

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs
from src.auth.tests.ads.conftest import insert_fake_ads, insert_fake_images

skip = False
# skip = True
reason = "Temporary off"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_list_ads_with_paginate(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    """Тест списка объявлений с пагинацией"""
    AMOUNT_ADS = 27
    SIZE = 5
    PAGE = 1

    await insert_fake_ads(amount_ads=AMOUNT_ADS)
    await insert_fake_images(amount_ads=AMOUNT_ADS)

    params = {"page": PAGE, "size": SIZE}

    resp = await client.get(routes.read_ads, params=params)
    log.debug(resp)
    data = resp.json()
    log.debug("список объявлений с пагинацией..", o=data)
    assert resp.status_code == 200
    assert data.get("total") == AMOUNT_ADS + 1
    # assert len(data) == 2
    # return
    assert len(data.get("items")) == SIZE
    assert data.get("page") == PAGE
    assert data.get("size") == SIZE
