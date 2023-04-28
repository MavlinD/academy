import pytest
from httpx import AsyncClient
from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.conftest import Routs
from src.auth.helpers.tools import read_response

skip = False
# skip = True
reason = "Temporary off!"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_register(client: AsyncClient, routes: Routs) -> None:
    """Тест запроса на регистрацию"""
    user = {
        "username": config.TEST_USER_USERNAME,
        "email": config.TEST_USER_EMAIL,
        "password": config.TEST_USER_PASSWORD,
    }
    # сначала регистрируем пол-ля
    resp = await client.put(routes.register, json=user)
    data = resp.json()
    # log.debug("", o=data)
    assert resp.status_code == 201
    # проверка не валидности новой УЗ
    resp = await client.post(routes.token_obtain, data=user)
    data = resp.json()
    log.debug("", o=data)
    assert resp.status_code == 400
    assert data.get("detail") == f"User {user.get('username')} inactive"
    # return
    # делаем запрос токена для верификации
    resp = await client.get(routes.request_to_verify_email(email=str(config.TEST_USER_EMAIL)))
    # временный файл, создаётся в корне проекта, внесен в гитигнор, можно добавить автоудаление
    log.debug(resp)
    # return
    token = await read_response()
    log.debug(token)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 202
    resp = await client.get(routes.accept_verify_token(token=token))
    data = resp.json()
    log.debug("запрос подтверждения электронного адреса", o=data)
    # return
    assert resp.status_code == 200
    user = {
        "username": config.TEST_USER_USERNAME,
        "password": config.TEST_USER_PASSWORD,
    }
    # проверка валидности новой УЗ
    resp = await client.post(routes.token_obtain, data=user)
    assert resp.status_code == 200
