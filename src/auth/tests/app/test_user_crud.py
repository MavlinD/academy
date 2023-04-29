# type: ignore
from typing import Any, Dict

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa
from starlette import status

from src.auth.config import config
from src.auth.conftest import Routs
from src.auth.helpers.tools import check_resp
from src.auth.schemas.token import UserScheme

skip = False
# skip = True
reason = "Temporary off!"

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_get_user_by_ID(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
) -> None:
    """Тест запроса на получение св-в польз-ля по ID"""
    # log.debug(regular_user)
    # log.debug(regular_user.id)
    resp = await client.get(routes.request_read_user(regular_user.id), headers=superuser_auth_headers)
    # log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    # log.debug(dir(resp))
    # log.debug(resp.text)
    # return
    # data = check_resp(resp, 200)
    assert resp.status_code == 200
    log.debug("Запроса на получение св-в польз-ля", o=data)
    assert data.get("username") == config.TEST_USER_USERNAME


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_get_user_by_email(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
) -> None:
    """Тест запроса на получение св-в польз-ля по email"""
    resp = await client.get(routes.request_read_user(regular_user.email), headers=superuser_auth_headers)
    data = check_resp(resp, 200)
    assert data.get("username") == config.TEST_USER_USERNAME


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_get_user_by_username(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
) -> None:
    """Тест запроса на получение св-в польз-ля по username"""
    resp = await client.get(routes.request_read_user(regular_user.username), headers=superuser_auth_headers)
    data = check_resp(resp, 200)
    assert data.get("username") == config.TEST_USER_USERNAME


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_get_user_without_superuser_access(
    client: AsyncClient,
    routes: Routs,
    user_active_auth_headers: Headers,
) -> None:
    """Тест запроса на получение св-в польз-ля обычным пол-лем"""
    resp = await client.get(
        routes.request_read_user(config.FIRST_USER_USERNAME),
        headers=user_active_auth_headers,
    )
    assert check_resp(resp, 403)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_get_fake_user(client: AsyncClient, routes: Routs, superuser_auth_headers: Headers) -> None:
    """Тест запроса на получение св-в несуществующего пол-ля"""
    resp = await client.get(routes.request_read_user("fake str id"), headers=superuser_auth_headers)
    log.debug(resp)
    log.debug(resp.json())
    assert check_resp(resp, 404)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_can_not_create_user_with_weak_password(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
) -> None:
    """Тест на невозможность создания пользователя с паролем не отвечающем условиям без-ти"""
    payload = {
        "username": "next",
        "email": config.TEST_USER_EMAIL,
        "password": "Pass567",
    }
    resp = await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("пароль слабый или содержит недопустимые символы", o=data)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_can_not_create_user_with_cyrillic_password(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
) -> None:
    """Тест на невозможность создания пользователя с кирилицей в пароле"""
    payload = {
        "username": "next",
        "email": config.TEST_USER_EMAIL,
        "password": "Пароль!567",
    }
    resp = await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("пароль слабый или содержит недопустимые символы", o=data)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_can_not_create_user_if_is_exist(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
) -> None:
    """Тест на невозможность создания пользователя с одинаковыми именами или почтой"""
    payload: Dict[str, Any] = {
        "username": "next",
        "email": config.TEST_USER_EMAIL,
        "password": "Pass@567",
    }
    resp = await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)
    assert check_resp(resp, 400)

    payload = {
        "username": config.TEST_USER_USERNAME,
        "email": "next@loc.loc",
        "password": "Pass#567",
    }
    resp = await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)
    assert check_resp(resp, 400)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_delete_user_by_email(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
) -> None:
    """Тест запроса на удаление польз-ля по email"""
    resp = await client.delete(
        routes.request_to_delete_user(str(config.TEST_USER_EMAIL)),
        headers=superuser_auth_headers,
    )
    check_resp(resp, 204)
    resp = await client.get(
        routes.request_read_user(str(config.TEST_USER_USERNAME)),
        headers=superuser_auth_headers,
    )
    check_resp(resp, 404)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_delete_user_by_username(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
) -> None:
    """Тест запроса на удаление польз-ля по username"""
    resp = await client.delete(
        routes.request_to_delete_user(str(config.TEST_USER_USERNAME)),
        headers=superuser_auth_headers,
    )
    check_resp(resp, 204)
    resp = await client.get(
        routes.request_read_user(str(config.TEST_USER_USERNAME)),
        headers=superuser_auth_headers,
    )
    check_resp(resp, 404)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_delete_user_by_id(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
) -> None:
    """Тест запроса на удаление польз-ля по id"""
    resp = await client.delete(routes.request_to_delete_user(regular_user.id), headers=superuser_auth_headers)
    check_resp(resp, 204)
    resp = await client.get(
        routes.request_read_user(str(config.TEST_USER_USERNAME)),
        headers=superuser_auth_headers,
    )
    check_resp(resp, 404)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_cant_delete_not_exist_user(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
) -> None:
    """Тест запроса на удаление несуществующего польз-ля"""
    resp = await client.delete(routes.request_to_delete_user("fake username"), headers=superuser_auth_headers)
    check_resp(resp, 404)
