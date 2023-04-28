import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa
from starlette import status

from src.auth.conftest import Routs

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)

skip = False
# skip = True
reason = "Временно отключен"


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_password(client: AsyncClient, routes: Routs, superuser_auth_headers: Headers) -> None:
    """Тест валидации исх данных на создание пользователя"""
    payload = {
        "username": "next",
        "email": "next@loc.loc",
        "password": "Pass567++",
        "is_superuser": False,
        "is_active": True,
        "is_active": True,
    }
    resp = await client.put(routes.create_user, json=payload, headers=superuser_auth_headers)
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    log.debug("-", o=data)
    resp = await client.get(routes.request_read_user(data.get("username")), headers=superuser_auth_headers)
    data = resp.json()
    log.debug("-", o=data)
    # return
    assert data.get("username") == payload.get("username")
    assert data.get("is_superuser") == payload.get("is_superuser")
    assert data.get("is_active") == payload.get("is_active")
