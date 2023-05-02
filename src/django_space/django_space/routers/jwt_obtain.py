from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from logrich.logger_ import log  # noqa

from src.auth.assets import APIRouter
from src.auth.config import config
from src.auth.schemas.token import RefreshToken, UserScheme
from src.auth.users.init import get_jwt_strategy, get_user_manager
from src.auth.users.security.jwt_actions import JWTStrategy
from src.auth.users.user_manager import UserManager

router = APIRouter()

unauthorized_responses: OpenAPIResponseType = {
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Missing token or inactive user.",
    }
}

login_responses: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.LOGIN_BAD_CREDENTIALS: {
                        "summary": "Bad credentials or the user is inactive.",
                        "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                    },
                    ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                        "summary": "The user is not verified.",
                        "value": {"detail": ErrorCode.LOGIN_USER_NOT_VERIFIED},
                    },
                }
            }
        },
    },
    status.HTTP_200_OK: {
        "description": f"Возвращает два токена: access & refresh. При этом срок годности access составляет "
        f"{config.JWT_ACCESS_KEY_EXPIRES_TIME_MINUTES} минут. "
        f"Refresh - {config.JWT_REFRESH_KEY_EXPIRES_TIME_DAYS} дней.",
        "content": {
            "application/json": {
                "example": {
                    "access": "aaa.bbb.ccc",
                    "refresh": "aaa.bbb.ccc",
                }
            },
        },
    },
}


@router.post("/token-obtain", responses=login_responses, response_model=RefreshToken)
async def token_obtain(
    credentials: OAuth2PasswordRequestForm = Depends(),
    jwt: JWTStrategy = Depends(get_jwt_strategy),
    user_manager: UserManager = Depends(get_user_manager),
) -> RefreshToken:
    """JWT obtain endpoint"""
    user = await user_manager.authenticate_user(credentials=credentials)
    active_user = await UserScheme.from_orms(user)
    access_token = await jwt.write_token(active_user, token_type="access")
    refresh_token = await jwt.write_token(
        active_user, token_type="refresh", days=config.JWT_REFRESH_KEY_EXPIRES_TIME_DAYS
    )
    return RefreshToken(
        access_token=access_token,
        refresh_token=refresh_token,
    )
