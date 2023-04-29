import typing

from fastapi import Depends, Request, status
from fastapi.params import Path
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from logrich.logger_ import log  # noqa
from pydantic import EmailStr

from src.auth.assets import APIRouter
from src.auth.handlers.errors.codes import none_message_response
from src.auth.schemas.user import PasswordReset, UserAttr
from src.auth.users.init import get_user_manager
from src.auth.users.user_manager import UserManager

router = APIRouter()

RESET_PASSWORD_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.RESET_PASSWORD_BAD_TOKEN: {
                        "summary": "Bad or expired token.",
                        "value": {"detail": ErrorCode.RESET_PASSWORD_BAD_TOKEN},
                    },
                    ErrorCode.RESET_PASSWORD_INVALID_PASSWORD: {
                        "summary": "Password validation failed.",
                        "value": {
                            "detail": {
                                "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                                "reason": "Password should be at least 3 characters",
                            }
                        },
                    },
                }
            }
        },
    },
    status.HTTP_200_OK: {"content": None},
}


@router.get(
    "/request-to-reset-password/{email:str}",
    status_code=status.HTTP_202_ACCEPTED,
    responses=none_message_response,
)
@typing.no_type_check
async def request_to_reset_password(
    email: EmailStr = Path(
        ...,
        description="на указанный адрес будет доставлена ссылка для изменения пароля",
    ),
    user_manager: UserManager = Depends(get_user_manager),
) -> None:
    user_attr = UserAttr(attr=email)
    user = await user_manager.get_user_by_uniq_attr(user_attr=user_attr)
    await user_manager.forgot_password(user)


@router.patch("/reset-password", responses=RESET_PASSWORD_RESPONSES)
async def reset_password(
    request: Request,
    payload: PasswordReset,
    user_manager: UserManager = Depends(get_user_manager),
) -> None:
    await user_manager.reset_password(payload=payload, request=request)
    return None
