from fastapi import Depends, status
from logrich.logger_ import log  # noqa

from src.auth.assets import APIRouter
from src.auth.schemas.token import UserScheme
from src.auth.schemas.user import UserUpdate
from src.auth.users.dependencies import get_current_active_user
from src.auth.users.init import get_user_manager
from src.auth.users.user_manager import UserManager

router = APIRouter()


@router.get(
    "/",
    response_model=UserScheme,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
    },
)
async def read_me(
    user: UserScheme = Depends(get_current_active_user),
) -> UserScheme:
    """get current user"""
    resp = await UserScheme.from_orms(user)
    return resp


@router.patch(
    "/",
    response_model=UserScheme,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
    },
)
async def update_me(
    user_update: UserUpdate,
    user: UserScheme = Depends(get_current_active_user),
    user_manager: UserManager = Depends(get_user_manager),
) -> UserScheme:
    """update current user"""
    ret = await user_manager.update_user_in_db(
        user=user,
        username=user.username,
        **user_update.dict(exclude_unset=True, exclude_none=True, include={"first_name", "last_name"})
    )
    resp = await UserScheme.from_orms(ret)
    return resp
