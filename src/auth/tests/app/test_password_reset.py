import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from logrich.logger_ import log  # noqa
from starlette import status

from src.auth.config import config
from src.auth.conftest import Routs
from src.auth.helpers.tools import read_response
from src.auth.schemas.token import UserScheme

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)

skip = False
# skip = True
reason = "Temporary off!"


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_password_reset(
    app: FastAPI,
    client: AsyncClient,
    routes: Routs,
    regular_user_active: UserScheme,
) -> None:
    """Тест запроса ссылки на смену пароля"""
    resp = await client.get(routes.request_to_reset_password(str(config.TEST_USER_EMAIL)))
    log.debug(resp)
    data = resp.json()
    log.debug("", o=data)
    # return
    assert resp.status_code == status.HTTP_202_ACCEPTED
    token = await read_response()
    new_pass = "newPass123#"
    # запрос с плохим токеном
    payload = {"token": token, "password": new_pass}
    # меняем пароль
    resp = await client.patch(routes.reset_password, json=payload)
    data = resp.json()
    log.debug("", o=data)
    # return
    assert resp.status_code == 200
    # проверим действие нового пароля
    payload = {"username": str(config.TEST_USER_EMAIL), "password": new_pass}
    resp = await client.post(routes.token_obtain, data=payload)
    data = resp.json()
    log.debug("", o=data)
    assert resp.status_code == 200


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_password_reset_invalid_responses(app: FastAPI, client: AsyncClient, routes: Routs) -> None:
    """Тест точки смены пароля, невалидные запросы"""
    resp = await client.get(routes.request_to_reset_password("some-str"))
    data = resp.json()
    assert data.get("detail") == [
        {
            "loc": ["path", "email"],
            "msg": "value is not a valid email address",
            "type": "value_error.email",
        }
    ]
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    user = "some-user@fake.com"
    resp = await client.get(routes.request_to_reset_password(user))
    data = resp.json()
    log.debug("", o=data)
    # return
    assert data.get("detail") == f"User {user} не существует"
    # временный файл, создаётся в корне проекта, внесен в гитигнор, можно добавить автоудаление
    token = await read_response()
    new_pass = "newPass123#"
    # запрос с плохим токеном
    payload = {"token": "fake token", "password": new_pass}
    resp = await client.patch(routes.reset_password, json=payload)
    assert resp.status_code in [422, 400]
    # еще один запрос с плохим токеном
    payload = {"token": "fake" * 52, "password": new_pass}
    resp = await client.patch(routes.reset_password, json=payload)
    assert resp.status_code == 422
    # запрос с невалидным паролем
    payload = {"token": token, "password": "123"}
    resp = await client.patch(routes.reset_password, json=payload)
    assert resp.status_code == 422
