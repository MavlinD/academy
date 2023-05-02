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
async def test_list_ads_with_paginate(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers, add_test_ad: Callable
) -> None:
    """Тест списка объявлений с пагинацией"""
    resp = await client.get(routes.read_ads)
    log.debug(resp)
    data = resp.json()
    log.debug("список объявлений", o=data)
    assert resp.status_code == 200
    assert len(data) == 2
