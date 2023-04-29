from django.contrib.auth.models import User
from fastapi import Body, Depends, status
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from logrich.logger_ import log  # noqa

from src.auth.assets import APIRouter
from src.auth.schemas.token import TokenRequest, UserScheme
from src.auth.users.init import get_user_manager
from src.auth.users.user_manager import UserManager

router = APIRouter()

login_responses: OpenAPIResponseType = {
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "example": {
                    "detail": ErrorCode.VERIFY_USER_BAD_TOKEN,
                }
            }
        },
    },
}


@router.post("/token-verify", responses=login_responses, response_model=UserScheme)
async def token_verify(
    token: TokenRequest = Body(...),
    user_manager: UserManager = Depends(get_user_manager),
) -> UserScheme:
    """Верификация токена"""
    user: User = await user_manager.jwt_verify(token.token)
    ret = await UserScheme.from_orms(user)
    return ret
