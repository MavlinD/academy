import pytest
from httpx import AsyncClient
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs

skip = False
# skip = True
reason = "Temporary off!"

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.parametrize("article,code", [("structure", 200)])
@pytest.mark.asyncio
async def test_wiki(client: AsyncClient, routes: Routs, article: str, code: int) -> None:
    """Тест получения страниц помощи 1"""
    await get_wiki(client, routes, article, code)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.parametrize("article,code", [("products", 200)])
@pytest.mark.asyncio
async def test_wiki2(client: AsyncClient, routes: Routs, article: str, code: int) -> None:
    """Тест получения страниц помощи 2"""
    await get_wiki(client, routes, article, code)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.parametrize("article,code", [("unexists_article", 404)])
@pytest.mark.asyncio
async def test_wiki3(client: AsyncClient, routes: Routs, article: str, code: int) -> None:
    """Тест получения страниц помощи 3"""
    await get_wiki(client, routes, article, code)


async def get_wiki(client: AsyncClient, routes: Routs, article: str, code: int) -> None:
    """Тест получения помощи main"""
    log.debug(article)
    resp = await client.get(routes.request_to_wiki_structure(article=article))
    # log.debug(resp)
    assert resp.status_code == code
