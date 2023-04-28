import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.conftest import Routs
from src.auth.schemas.user import UserAttr

# from starlette import status


skip = False
# skip = True
reason = "Временно отключен"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_update_user_without_pass(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    user_active_auth_headers: UserAttr,
) -> None:
    """Тест неизменности пароля в тесте на обновление пользователя"""
    payload = {
        "first_name": "Пал Андреич",
        "password": "Http%500",
    }
    resp = await client.patch(
        routes.request_to_update_user(str(config.TEST_USER_USERNAME)),
        json=payload,
        headers=superuser_auth_headers,
    )
    data = resp.json()
    log.debug("", o=data)
    # return
    assert resp.status_code == 200
    user = {
        "username": config.TEST_USER_USERNAME,
        "password": config.TEST_USER_PASSWORD,
    }
    resp = await client.post(routes.token_obtain, data=user)
    log.debug(resp)
    data = resp.json()
    log.debug("запрос со старым паролем", o=data)
    assert resp.status_code == 200


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "attr, payload, is_active",
    [
        (
            "username",
            {},
            True,
        )
    ],
)
async def test_cant_update_user_under_superuser(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    user_active_auth_headers: UserAttr,
    attr: str,
    payload: dict,
    is_active: bool,
) -> None:
    """Тест на обновление несуществующего пользователя"""
    await update_regular_user_under_superuser(
        client=client,
        routes=routes,
        superuser_auth_headers=superuser_auth_headers,
        attr=attr,
        payload=payload,
        is_active=is_active,
        status=404,
    )


async def update_regular_user_under_superuser(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    attr: str,
    payload: dict,
    is_active: bool,
    status: int = 200,
) -> None:
    """Тест на обновление обычного пользователя суперпользователем по имени"""
    payload |= {
        "first_name": "Пал Андреич",
        "last_name": "Кольцов",
        "is_staff": True,
        "is_superuser": False,
        "password": "Http^500",
    }
    log.debug("", o=payload)

    resp = await client.patch(
        routes.request_to_update_user("fake-user"),
        json=payload,
        headers=superuser_auth_headers,
    )
    data = resp.json()
    log.debug("-", o=data)
    assert resp.status_code == status
    return

    resp = await client.get(routes.request_read_user(data.get("username")), headers=superuser_auth_headers)
    data = resp.json()
    log.debug("", o=data)
    assert data.get("first_name") == payload.get("first_name")
    # если почта была в нагрузке
    email = payload.get("email")
    if email:
        assert data.get("email") == payload.get("email")
    assert data.get("is_active") == is_active
    assert data.get("is_superuser") is False
    assert data.get("is_staff") is True
    # return

    # если активный статус поль-ля не изменился:
    if is_active:
        user = {
            "username": config.TEST_USER_USERNAME,
            "password": config.TEST_USER_PASSWORD,
        }
        resp = await client.post(routes.token_obtain, data=user)
        data = resp.json()
        log.debug("запрос со старым паролем", o=data)
        assert resp.status_code == status
