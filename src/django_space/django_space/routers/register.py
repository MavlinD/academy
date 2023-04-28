from fastapi import Depends, status
from fastapi_users.router.common import ErrorCode, ErrorModel
from logrich.logger_ import log  # noqa

from src.auth.assets import APIRouter
from src.auth.schemas.token import UserScheme
from src.auth.schemas.user import UserCreate
from src.auth.users.init import get_user_manager
from src.auth.users.user_manager import UserManager

router = APIRouter()


@router.put(
    "/register",
    response_model=UserScheme,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {"detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS},
                        },
                        ErrorCode.REGISTER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                    "reason": "Password should be" "at least 3 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def register(
    user_create: UserCreate,
    user_manager: UserManager = Depends(get_user_manager),
) -> UserScheme:
    """Регистрация пользователя"""
    user = await user_manager.put_user_in_db(
        **user_create.dict(exclude={"is_superuser", "is_staff", "is_active"}, exclude_unset=True), is_active=False
    )

    return user
