from fastapi import Depends, status
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from logrich.logger_ import errlog, log  # noqa

from src.auth.assets import APIRouter
from src.auth.config import config
from src.auth.handlers.errors.codes import ErrorCodeLocal
from src.auth.schemas.token import RefreshToken, TokenRequest, UserScheme
from src.auth.users.init import get_jwt_strategy, get_user_manager
from src.auth.users.security.jwt_actions import JWTStrategy
from src.auth.users.user_manager import UserManager

router = APIRouter()

login_responses: OpenAPIResponseType = {
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "example": {
                    "detail": ErrorCodeLocal.REFRESH_USER_BAD_TOKEN,
                }
            }
        },
    },
}


@router.post(
    "/token-refresh",
    responses=login_responses,
    response_model=RefreshToken,
)
async def token_refresh(
    payload: TokenRequest,
    jwt: JWTStrategy = Depends(get_jwt_strategy),
    user_manager: UserManager = Depends(get_user_manager),
) -> RefreshToken:
    """Запрос на обновление пары токенов"""
    user: UserScheme = await user_manager.jwt_verify(payload.token)
    if user:
        access_token = await jwt.write_token(user, token_type="access")
        refresh_token = await jwt.write_token(
            user, token_type="refresh", days=config.JWT_REFRESH_KEY_EXPIRES_TIME_DAYS
        )
        return RefreshToken(
            access_token=access_token,
            refresh_token=refresh_token,
        )
