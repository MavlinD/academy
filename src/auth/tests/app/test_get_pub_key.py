import pytest
from httpx import AsyncClient
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs

skip = False
# skip = True
reason = "Temporary off!"

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_pub_key(client: AsyncClient, routes: Routs) -> None:
    """Тест запроса на получение публичного ключа"""
    resp = await client.get(routes.read_pub_key)
    log.debug(resp.text)
    assert resp.status_code == 200


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_home_page(client: AsyncClient, routes: Routs) -> None:
    """Тест запроса домашней страницы"""
    resp = await client.get(routes.read_home)
    # print(resp.text)
    assert resp.status_code == 200
