import typing
from datetime import timedelta
from typing import Any, List, Optional

import jwt
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from django.db.models import Q, QuerySet
from fastapi.security import OAuth2PasswordRequestForm
from logrich.logger_ import log  # noqa
from pydantic import EmailStr
from starlette.requests import Request

from src.auth.config import config
from src.auth.helpers.email import (
    send_password_reset_email,
    send_verification_email,
    write_response,
)
from src.auth.schemas.request import EmailSchema, UsersFilter
from src.auth.schemas.token import UserScheme
from src.auth.schemas.user import PasswordReset, UserAttr, UserCreate, UserUpdate
from src.auth.users.exceptions import (
    InvalidCredentials,
    InvalidResetPasswordToken,
    InvalidVerifyToken,
    UserAlreadyExists,
    UserAlreadyVerified,
    UserInactive,
    UserNotExists,
)
from src.auth.users.security.jwt_tools import SecretType, decode_jwt, generate_jwt
from src.auth.users.security.password import PasswordHelper
from asgiref.sync import async_to_sync, sync_to_async


class UserManager:
    reset_password_token_secret: SecretType = config.PRIVATE_KEY
    reset_password_token_lifetime_seconds: int = config.RESET_PASSWORD_TOKEN_LIFETIME_SECONDS

    verification_token_secret: SecretType = config.PRIVATE_KEY
    verification_token_lifetime_seconds: int = config.VERIFICATION_TOKEN_LIFETIME_SECONDS

    reset_password_token_audience: str = "fastapi-users:reset"
    verification_token_audience: str = config.TOKEN_AUDIENCE_VERIFY
    password_helper: PasswordHelper

    def __init__(
        self,
        password_helper: Any = None,
    ):
        self.user_model = get_user_model()

        if password_helper is None:
            self.password_helper = PasswordHelper()
        else:
            self.password_helper = password_helper  # pragma: no cover

    async def on_after_register(self, user: UserScheme) -> None:
        if user:
            log.info(
                f"User {user.id} has registered.",  # type: ignore
                o=user.dict(
                    include={
                        "username",
                        "email",
                        "is_superuser",
                        "is_active",
                        "is_active",
                    },
                ),
            )
            # выполним запрос на верификацию УЗ, чтобы отослать письмо на подтверждение эл.почты
            user_ = await UserScheme.from_orms(user)
            await self.request_verify(user_)

    @staticmethod
    async def on_after_forgot_password(user: UserScheme, token: str) -> None:
        email = EmailSchema(email=[user.email], body={"token": token})  # type: ignore
        await send_password_reset_email(email=email)
        log.info(f"User {user.id} has forgot their password. Reset token: {token}")  # type: ignore
        await write_response(token)

    @staticmethod
    async def on_after_request_verify(user: UserScheme, token: str) -> None:
        email = EmailSchema(email=[user.email], body={"token": token})  # type: ignore
        await send_verification_email(email=email)
        await write_response(token)

    async def list_users(self, params: UsersFilter) -> List[UserScheme]:
        """get all users with filters, AND conditions"""
        filter_ = params.dict(exclude_none=True, exclude_unset=True)
        users = self.user_model.objects.all().filter(**filter_)
        return users

    async def list_users_v2(self, params: UsersFilter) -> QuerySet:
        """get all users with filters, AND & OR conditions"""
        users = self.user_model.objects.all()
        or_qparams = Q()
        and_qparams = Q()

        if params.groups:
            and_qparams &= Q(groups__in=params.groups)
        if params.users:
            and_qparams &= Q(id__in=params.users)
        if params.is_staff is not None:
            and_qparams &= Q(is_staff=params.is_staff)
        if params.is_active is not None:
            and_qparams &= Q(is_active=params.is_active)
        if params.is_superuser is not None:
            and_qparams &= Q(is_superuser=params.is_superuser)

        if params.search:
            or_qparams |= Q(username__icontains=params.search)
        if params.search:
            or_qparams |= Q(email__icontains=params.search)
        if params.search:
            or_qparams |= Q(first_name__icontains=params.search)
        if params.search:
            or_qparams |= Q(last_name__icontains=params.search)

        if params.username:
            or_qparams |= Q(username__icontains=params.username)
        if params.email:
            or_qparams |= Q(email__icontains=params.email)
        if params.first_name:
            or_qparams |= Q(first_name__icontains=params.first_name)
        if params.last_name:
            or_qparams |= Q(last_name__icontains=params.last_name)

        qparams = and_qparams & or_qparams
        # log.debug("qparams", o=qparams)
        users = await sync_to_async(users.filter)(qparams)
        return users

    @typing.no_type_check
    async def request_verify(self, user: User) -> None:
        """Start a verification request."""
        if user.is_active:
            raise UserAlreadyVerified(user=user)
        token_data: dict[str, object] = {
            "type": "access",
            "username": user.username,
            "uid": str(user.id),
            "sub": "auth",
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        # log.debug(token_data)
        token = generate_jwt(
            data=token_data,
            secret=self.verification_token_secret,
            lifetime=timedelta(seconds=self.verification_token_lifetime_seconds),
        )
        await self.on_after_request_verify(user, token)

    async def update_user_in_db(
        self,
        user: User | UserScheme,
        username: str,
        email: EmailStr | None = None,
        is_superuser: bool | None = None,
        is_staff: bool | None = None,
        is_active: bool | None = None,
        first_name: str = "",
        last_name: str = "",
    ) -> User:
        """update user"""
        if email and user.email != email:  # type: ignore
            is_active = False
        update_payload = UserUpdate(
            email=email,
            is_superuser=is_superuser,
            is_staff=is_staff,
            is_active=is_active,
            first_name=first_name,
            last_name=last_name,
        )
        await self.user_model.objects.filter(
            username=username,
        ).aupdate(**update_payload.dict(exclude={"username"}, exclude_none=True, exclude_unset=True))
        user_response = await self.get_user_by_uniq_attr(UserAttr(attr=username))

        return user_response

    async def get_user_by_uniq_attr(self, user_attr: UserAttr) -> User | None:
        """get user by uniq user attr"""
        attr = user_attr.attr
        if isinstance(attr, str) and attr.isdigit():
            user_in_db = await self.user_model.objects.filter(pk=attr).afirst()
        else:
            user_in_db = await self.user_model.objects.filter(Q(username=attr) | Q(email=attr)).afirst()
        if not user_in_db:
            raise UserNotExists(user=str(attr))
        return user_in_db

    # flake8: noqa
    async def verify_email(self, token: str, request: Request | None = None) -> UserScheme:
        """Validate a verification request."""
        try:
            data = decode_jwt(
                token,
                self.verification_token_secret,
                [self.verification_token_audience],
            )
        except jwt.PyJWTError:
            raise InvalidVerifyToken()

        try:
            uid = data["uid"]
            email = data["email"]
        except KeyError:
            raise InvalidVerifyToken()
        try:
            user_attr = UserAttr(attr=email)
            user = await self.get_user_by_uniq_attr(user_attr=user_attr)
        except UserNotExists:
            raise InvalidVerifyToken()

        if uid != user.id:  # type: ignore
            raise InvalidVerifyToken()

        if user.is_active:  # type: ignore
            raise UserAlreadyVerified(user=user)

        verified_user: UserScheme = await self.update_user_in_db(user=user, username=user.username, is_active=True)  # type: ignore

        await self.on_after_verify(verified_user, request)

        return verified_user

    async def authenticate_user(self, credentials: OAuth2PasswordRequestForm) -> User | None:
        """аутентифицировать пользователя по username or email"""
        user_in_db = await self.get_user_by_uniq_attr(UserAttr(attr=credentials.username))
        if not user_in_db.is_active:  # type: ignore
            raise UserInactive(user=user_in_db)

        user: User = await sync_to_async(authenticate)(
            username=user_in_db.username,  # type: ignore
            password=credentials.password,
        )

        # log.debug(user)
        if not user:
            raise InvalidCredentials(msg=credentials.username)

        return user

    @typing.no_type_check
    async def forgot_password(self, user: UserScheme) -> None:
        """Start a forgot password request."""
        if not user.is_active:
            raise UserInactive(user=user)

        token_data: dict[str, object] = {
            "sub": "auth",
            "type": "access",
            "uid": str(user.id),
            "username": str(user.username),
            "email": str(user.email),
            "aud": self.reset_password_token_audience,
        }
        token = generate_jwt(
            data=token_data,
            secret=self.verification_token_secret,
            lifetime=timedelta(seconds=self.verification_token_lifetime_seconds),
        )

        await self.on_after_forgot_password(user, token)

    async def reset_password(self, payload: PasswordReset, request: Optional[Request] = None) -> User:
        try:
            data = decode_jwt(
                payload.token,
                self.reset_password_token_secret,
                [self.reset_password_token_audience],
            )
        except jwt.PyJWTError:
            raise InvalidResetPasswordToken(msg=payload.token)

        uid = data.get("uid")

        user_attr = UserAttr(attr=uid)
        user = await self.get_user_by_uniq_attr(user_attr=user_attr)

        if not user.is_active:
            raise UserInactive(user=user)

        user.set_password(payload.password)
        await sync_to_async(user.save)()

        await self.on_after_reset_password(user, request)  # type: ignore

        return user

    async def validate_password(self, password: str, user: UserScheme) -> None:
        """
        Validate a password.

        *You should overload this method to add your own validation logic.*

        :param password: The password to validate.
        :param user: The user associated to this password.
        :raises InvalidPasswordException: The password is invalid.
        :return: None if the password is valid.
        """
        return  # pragma: no cover

    async def on_after_update(
        self,
        user: UserScheme,
        update_dict: UserCreate,
    ) -> None:
        """
        Perform logic after successful user update.

        *You should overload this method to add your own logic.*

        :param user: The updated user
        :param update_dict: Dictionary with the updated user fields.
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_verify(self, user: UserScheme, request: Request | None = None) -> None:
        """
        Perform logic after successful user verification.

        *You should overload this method to add your own logic.*

        :param user: The verified user.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_reset_password(self, user: UserScheme, request: Optional[Request] = None) -> None:
        """
        Perform logic after successful password reset.

        *You should overload this method to add your own logic.*

        :param user: The user that reset its password.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def jwt_verify(self, token: str) -> UserScheme:
        """Validate JWT."""
        try:
            data = decode_jwt(token)
            user_attr = UserAttr(attr=data["uid"])
            user: User = await self.get_user_by_uniq_attr(user_attr=user_attr)
            uid = data.get("uid")
            if uid != user.id:
                raise InvalidVerifyToken(msg=token)
            ret = await UserScheme.from_orms(user)
            return ret

        except (ValueError, jwt.PyJWTError) as err:
            if hasattr(err, "detail"):
                raise InvalidVerifyToken(msg=getattr(err, "detail"))
            else:
                raise InvalidVerifyToken(msg=err)

    async def put_user_in_db(
        self,
        username: str,
        email: EmailStr,
        password: str,
        is_superuser: bool = False,
        is_staff: bool = False,
        is_active: bool = True,
        first_name: str = "",
        last_name: str = "",
    ) -> User:
        """create user"""
        user_scheme = UserScheme(
            username=username,
            email=email,
        )
        await self.is_user_not_in_db(user=user_scheme)
        user = await sync_to_async(self.user_model.objects.create_user)(
            username=username,
            email=email,
            password=password,
            is_superuser=is_superuser,
            is_staff=is_staff,
            is_active=is_active,
            first_name=first_name,
            last_name=last_name,
        )
        # user.save()
        return user

    @typing.no_type_check
    async def is_user_not_in_db(self, user: UserScheme) -> bool:
        """check user not in db"""
        user_in_db = await self.user_model.objects.filter(Q(username=user.username) | Q(email=user.email)).aexists()
        if user_in_db:
            raise UserAlreadyExists(user=user)
        return True

    @typing.no_type_check
    async def is_user_in_db(self, user: UserScheme) -> bool:
        """check user in db"""
        user_in_db = await self.user_model.objects.filter(Q(username=user.username) | Q(email=user.email)).aexists()
        if not user_in_db:
            raise UserNotExists(user=user)
        return True

    async def remove_user(self, user: User) -> None:
        """remove user"""
        await self.user_model.objects.filter(username=user.username).adelete()
