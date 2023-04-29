# type: ignore
from typing import Callable

import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa
from starlette import status

from src.auth.config import config
from src.auth.conftest import Routs
from src.auth.schemas.token import UserScheme

skip = False
# skip = True
reason = "Temporary off!"

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_get_user_with_groups(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
    create_group_fixture: Callable,
) -> None:
    """Тест на получение пользователя с выводом группы в ответе"""
    # log.debug(regular_user)
    # return
    payload = {
        "group_attr": config.TEST_GROUP,
        "user_attr": regular_user.username,
    }
    # log.debug(payload)
    resp = await client.patch(
        routes.request_move_in_out_group(action="add"),
        json=payload,
        headers=superuser_auth_headers,
    )
    data = resp.json()
    log.debug("-", o=data)
    # return
    resp = await client.get(
        routes.request_read_user(user_attr=regular_user.email),
        headers=superuser_auth_headers,
    )
    data = resp.json()
    log.debug("запроса на получение св-в польз-ля включая группы", o=data)
    # return
    assert data["groups"][0]["name"] == config.TEST_GROUP
    assert data.get("username") == config.TEST_USER_USERNAME


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_move_user_to_group(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
    create_group_fixture: Callable,
) -> None:
    """Тест на перемещение пользователя в группу и вывод группы в ответе"""
    payload = {
        "group_attr": config.TEST_GROUP,
        "user_attr": regular_user.username,
    }
    resp = await client.patch(
        routes.request_move_in_out_group(action="add"),
        json=payload,
        headers=superuser_auth_headers,
    )
    data = resp.json()
    log.debug("-", o=data)
    assert data["groups"][0]["name"] == config.TEST_GROUP
    # return
    resp = await client.get(routes.read_groups, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("", o=data)
    # return
    assert data[0]["user_set"][0]["username"] == config.TEST_USER_USERNAME
    payload = {
        "group_attr": config.TEST_GROUP,
        "user_attr": regular_user.username,
    }
    resp = await client.patch(
        routes.request_move_in_out_group(action="remove"),
        json=payload,
        headers=superuser_auth_headers,
    )
    data = resp.json()
    log.debug("групп быть не должно", o=data)
    assert len(data["groups"]) == 0


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_move_user_to_group_by_id(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
    create_group_fixture: Callable,
) -> None:
    """Тест на перемещение пользователя по ID, email в группу и вывод группы в ответе"""
    payload = {
        "group_attr": 1,
        "user_attr": 1,
    }
    resp = await client.patch(
        routes.request_move_in_out_group(action="add"),
        json=payload,
        headers=superuser_auth_headers,
    )
    data = resp.json()
    log.debug("-", o=data)
    assert data["groups"][0]["name"] == config.TEST_GROUP
    # return
    resp = await client.get(routes.read_groups, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("", o=data)
    # return
    assert data[0]["user_set"][0]["username"] == config.FIRST_USER_USERNAME
    payload = {
        "group_attr": 1,
        "user_attr": config.TEST_USER_EMAIL,
    }
    resp = await client.patch(
        routes.request_move_in_out_group(action="remove"),
        json=payload,
        headers=superuser_auth_headers,
    )
    data = resp.json()
    log.debug("групп быть не должно", o=data)
    assert len(data["groups"]) == 0


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_cant_use_not_permited_action(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
    create_group_fixture: Callable,
) -> None:
    """Тест на невозможность запроса с произвольным действием"""
    payload = {
        "group_attr": config.TEST_GROUP,
        "user_attr": regular_user.username,
    }
    resp = await client.patch(
        routes.request_move_in_out_group(action="fake-action"),
        json=payload,
        headers=superuser_auth_headers,
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = resp.json()
    log.debug("-", o=data)
