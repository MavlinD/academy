# type: ignore
import pytest
from httpx import AsyncClient
from logrich.logger_ import log

from src.auth.config import config
from src.auth.conftest import Routs

skip = False
# skip = True
reason = "Temporary off!"

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_verify_token(client: AsyncClient, routes: Routs) -> None:
    """Тест запроса на верификацию токена"""
    # валидируем по email
    user = {
        "username": config.FIRST_USER_EMAIL,
        "password": config.FIRST_USER_PASSWORD,
    }
    resp = await client.post(routes.token_obtain, data=user)
    log.debug(resp)
    data = resp.json()
    # log.debug("-", o=data)
    payload = {"token": data.get("access_token")}
    resp = await client.post(routes.token_verify, json=payload)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 200

    # валидируем по имени
    user = {
        "username": config.FIRST_USER_USERNAME,
        "password": config.FIRST_USER_PASSWORD,
    }
    resp = await client.post(routes.token_obtain, data=user)
    log.debug(resp)
    data = resp.json()
    # log.debug("-", o=data)
    payload = {"token": data.get("access_token")}
    resp = await client.post(routes.token_verify, json=payload)
    data = resp.json()
    log.debug("", o=data)
    assert resp.status_code == 200


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_verify_invalid_token(client: AsyncClient, routes: Routs) -> None:
    """Тест верификации поддельного токена"""
    payload = {"token": "aaa.bbb.ccc"}
    resp = await client.post(routes.token_verify, json=payload)
    data = resp.json()
    log.debug(data)
    assert resp.status_code == 422
