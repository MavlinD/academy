from fastapi import Depends, Path, Request, status
from fastapi_users.router.common import ErrorCode, ErrorModel
from logrich.logger_ import log  # noqa
from pydantic import EmailStr

from src.auth.assets import APIRouter
from src.auth.schemas.token import UserScheme
from src.auth.schemas.user import UserAttr
from src.auth.users.init import get_user_manager
from src.auth.users.user_manager import UserManager

router = APIRouter()


@router.get(
    "/request-for-verify/{email:str}",
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_to_verify_email(
    email: EmailStr = Path(
        ...,
        description="на указанный адрес будет доставлено письмо со ссылкой на подтверждение",
    ),
    user_manager: UserManager = Depends(get_user_manager),
) -> None:
    """Запрос письма с токеном для верификации УЗ.
    Обычно письмо с запросом отправляется автоматически после регистрации, но можно запросить его повторно.
    """
    user_attr = UserAttr(attr=email)
    user_in_db = await user_manager.get_user_by_uniq_attr(user_attr=user_attr)
    await user_manager.request_verify(user=user_in_db)


@router.get(
    "/accept-verify-token/{token:str}",
    response_model=UserScheme,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.VERIFY_USER_BAD_TOKEN: {
                            "summary": "Bad token, not existing user or" "not the e-mail currently set for the user.",
                            "value": {"detail": ErrorCode.VERIFY_USER_BAD_TOKEN},
                        },
                        ErrorCode.VERIFY_USER_ALREADY_VERIFIED: {
                            "summary": "The user is already verified.",
                            "value": {"detail": ErrorCode.VERIFY_USER_ALREADY_VERIFIED},
                        },
                    }
                }
            },
        }
    },
)
async def accept_verify_token(
    request: Request,
    token: str = Path(
        ...,
        description="требуется токен предоставленный после регистрации пользователя",
    ),
    user_manager: UserManager = Depends(get_user_manager),
) -> UserScheme:
    """Верификация новой УЗ"""
    user = await user_manager.verify_email(token, request)
    resp = await UserScheme.from_orms(user)
    return resp
