import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs
from src.auth.schemas.token import UserScheme

# skip = False
skip = True
reason = "Временно отключен"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.parametrize("is_superuser", [False])
@pytest.mark.asyncio
async def test_self_update_regular_user(
    client: AsyncClient,
    routes: Routs,
    user_active_auth_headers: Headers,
    # regular_user: UserOutSUWithGroups,
    is_superuser: bool,
) -> None:
    """Тест на самообновление обычного пользователя"""
    await update_user(client, routes, user_headers=user_active_auth_headers, is_superuser=is_superuser)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.parametrize("is_superuser", [True])
@pytest.mark.asyncio
async def test_self_update_super_user(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    regular_user: UserScheme,
    is_superuser: bool,
) -> None:
    """Тест на самообновление обычного пользователя"""
    await update_user(client, routes, user_headers=superuser_auth_headers, is_superuser=is_superuser)


async def update_user(client: AsyncClient, routes: Routs, user_headers: Headers, is_superuser: bool) -> None:
    """Тест на самообновление обычного пользователя"""
    payload = {
        "first_name": "Пал Андреич",
        "last_name": "Кольцов",
        "is_active": False,
        "is_superuser": True,
        "is_verified": False,
    }
    resp = await client.patch(
        routes.update_me,
        json=payload,
        headers=user_headers,
    )
    data = resp.json()
    log.debug("", o=data)
    resp = await client.get(routes.read_me, headers=user_headers)
    data = resp.json()
    log.debug("-", o=data)
    assert data.get("first_name") == payload.get("first_name")
    assert data.get("last_name") == payload.get("last_name")
    assert data.get("is_superuser") is is_superuser
    assert data.get("is_active") is True
