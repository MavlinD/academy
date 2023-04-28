import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.conftest import Routs

# skip = False
skip = True
reason = "Temporary off!!"

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_me(client: AsyncClient, routes: Routs, user_active_auth_headers: Headers) -> None:
    """Тест запроса на получение своих св-в"""
    resp = await client.get(routes.read_me, headers=user_active_auth_headers)
    # log.debug(resp)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 200
    assert data.get("username") == config.TEST_USER_USERNAME


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_me_inactive_user(client: AsyncClient, routes: Routs, user_unactive_auth_headers: Headers) -> None:
    """Тест запроса на получение своих св-в для неактивного пользователя"""
    resp = await client.get(routes.read_me, headers=user_unactive_auth_headers)
    assert resp.status_code == 401


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_patch_me(client: AsyncClient, routes: Routs, user_active_auth_headers: Headers) -> None:
    """Тест запроса на самообновление"""
    payload = {
        "first_name": "Петька",
        "last_name": "Горбунков",
        "email22": "next@loc.loc",
        "email": "next@loc.loc",
        "password": "Pass567++",
    }
    resp = await client.patch(routes.update_me, headers=user_active_auth_headers, json=payload)
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == 200
    assert data.get("last_name") == payload.get("last_name")
    assert data.get("email") != payload.get("email")
