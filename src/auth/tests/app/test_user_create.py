# type: ignore
from typing import Any, Dict

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.conftest import Routs
from src.auth.schemas.token import UserScheme

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)

skip = False
# skip = True
reason = "Temporary off!"


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_users(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
) -> None:
    """Тест на создание пользователя"""
    payload: Dict[str, Any] = {
        "username": "next",
        "email": "next@loc.loc",
        "password": "Pass!567",
        "is_superuser": False,
        "is_staff": False,
        "is_active": True,
    }
    resp = await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)

    log.debug(resp)
    assert resp.status_code == 201
    # return


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_similar_users(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
) -> None:
    """Тест вывода исключения на создание дубля пользователя"""
    payload: Dict[str, Any] = {
        "username": "next",
        "email": "next@loc.loc",
        "password": "Pass!567",
        "is_superuser": False,
        "is_staff": False,
        "is_active": True,
    }
    await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)
    resp = await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)
    log.debug(resp)
    data = resp.json()
    log.debug(data)
    assert data.get("detail", "").endswith("already exists")


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_users_with_too_short_username(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
) -> None:
    """Тест вывода исключения на создание пользователя со слишком коротким именем"""
    payload: Dict[str, Any] = {
        "username": "a",
        "email": "next@loc.loc",
        "password": "Pass!567",
        "is_superuser": False,
        "is_staff": False,
        "is_active": True,
    }
    resp = await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 422


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_users_with_novalid_email(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
) -> None:
    """Тест вывода исключения на создание пользователя с не валидной почтой"""
    payload: Dict[str, Any] = {
        "username": "foo",
        "email": "nextloc.loc",
        "password": "Pass!567",
        "is_superuser": False,
        "is_staff": False,
        "is_active": True,
    }
    resp = await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 422


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_users_with_no_any_attr(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
) -> None:
    """Тест на создание пользователя без указания атрибутов суперпользователя и обслуживающего персонала"""
    payload: Dict[str, Any] = {
        "username": "foo",
        "email": "next@loc.loc",
        "password": "Pass!567",
    }
    resp = await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 201


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_users_without_password(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
) -> None:
    """Тест на создание пользователя без указания пароля"""
    payload: Dict[str, Any] = {
        "username": "foo",
        "email": "next@loc.loc",
        # "password": "Pass!567",
    }
    resp = await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 422


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_create_users_with_weak_password(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
) -> None:
    """Тест на создание пользователя со слабым паролем"""
    payload: Dict[str, Any] = {
        "username": "foo",
        "email": "next@loc.loc",
        "password": "Pass567",
    }
    resp = await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 422


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_remove_user(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
) -> None:
    """Тест на удаления пользователя"""
    resp = await client.delete(
        routes.request_to_delete_user(config.TEST_USER_USERNAME), headers=superuser_auth_headers
    )
    log.debug(resp)
    data = resp.text
    log.debug("-", o=data)
    assert resp.status_code == 204
    # проверим существование
    resp = await client.get(routes.request_read_user(config.TEST_USER_USERNAME), headers=superuser_auth_headers)
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 404


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_cant_remove_self(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
) -> None:
    """Тест на само удаления пользователя"""
    resp = await client.delete(
        routes.request_to_delete_user(config.FIRST_USER_USERNAME), headers=superuser_auth_headers
    )
    log.debug(resp)
    data = resp.text
    log.debug("-", o=data)
    # return
    assert resp.status_code == 204
    # проверим существование
    payload = {
        "username": config.FIRST_USER_USERNAME,
        "password": config.FIRST_USER_PASSWORD,
    }
    resp = await client.post(routes.token_obtain, data=payload)
    log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 404
