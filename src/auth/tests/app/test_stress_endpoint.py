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
async def test_stress(client: AsyncClient, routes: Routs) -> None:
    """тест нагрузочного запроса"""
    resp = await client.get(routes.stress_test, params={"iterate": 5})
    # log.debug(resp)
    # return
    data = resp.json()
    log.debug("stress test..", o=data)
    assert resp.status_code == 200
