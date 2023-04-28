# type: ignore
import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.conftest import Routs
from src.auth.schemas.user import UserAttr

skip = False
# skip = True
reason = "Временно отключен"
pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "attr, payload, is_active",
    [
        (
            "username",
            {
                "email": "new@loc.loc",
                # новая почта должна сбросить статус юзера
                "is_active": True,
            },
            False,
        )
    ],
)
async def test_update_regular_user_under_superuser_by_username(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    user_active_auth_headers: UserAttr,
    attr: str,
    payload: dict,
    is_active: bool,
) -> None:
    """Тест на обновление обычного пользователя суперпользователем по имени"""
    await update_regular_user_under_superuser(
        client=client,
        routes=routes,
        superuser_auth_headers=superuser_auth_headers,
        attr=attr,
        payload=payload,
        is_active=is_active,
    )


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "attr, payload, is_active",
    [
        (
            "email",
            {
                "email": "test@loc.loc",
                # почта не меняется, соотвественно статус не должен сбросится
                "is_active": True,
            },
            True,
        )
    ],
)
async def test_update_regular_user_under_superuser_by_email(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    user_active_auth_headers: UserAttr,
    attr: str,
    payload: dict,
    is_active: bool,
) -> None:
    """Тест на обновление обычного пользователя суперпользователем по почте"""
    await update_regular_user_under_superuser(
        client=client,
        routes=routes,
        superuser_auth_headers=superuser_auth_headers,
        attr=attr,
        payload=payload,
        is_active=is_active,
    )


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "attr, payload, is_active",
    [
        (
            "uid",
            {
                "is_active": False,
            },
            False,
        )
    ],
)
async def test_update_regular_user_under_superuser_by_uid(
    client: AsyncClient,
    routes: Routs,
    superuser_auth_headers: Headers,
    user_active_auth_headers: UserAttr,
    attr: str,
    payload: dict,
    is_active: bool,
) -> None:
    """Тест на обновление обычного пользователя суперпользователем по ID"""
    await update_regular_user_under_superuser(
        client=client,
        routes=routes,
        superuser_auth_headers=superuser_auth_headers,
        attr=attr,
        payload=payload,
        is_active=is_active,
    )


async def update_regular_user_under_superuser(
    client: AsyncClient, routes: Routs, superuser_auth_headers: Headers, attr: str, payload: dict, is_active: bool
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
    param = None
    match attr:
        case "username":
            param = config.TEST_USER_USERNAME
        case "email":
            param = config.TEST_USER_EMAIL
        case "uid":
            param = 2
    resp = await client.patch(
        routes.request_to_update_user(str(param)),
        json=payload,
        headers=superuser_auth_headers,
    )
    data = resp.json()
    log.debug("-", o=data)

    resp = await client.get(routes.request_read_user(data.get("username")), headers=superuser_auth_headers)
    data = resp.json()
    # log.debug("", o=data)
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
        assert resp.status_code == 200
