from fastapi import HTTPException
from logrich.logger_ import log  # noqa
from starlette import status

from src.auth.schemas.token import UserScheme


class FastAPIUsersException(HTTPException):
    def __init__(self) -> None:
        self.detail: str = "Некорректный запрос"
        self.status_code: int = status.HTTP_400_BAD_REQUEST


class UserAlreadyExists(FastAPIUsersException):
    def __init__(self, user: UserScheme = None) -> None:
        if user:
            self.detail = f"User [cyan b]{user.username}[/] or [cyan b]{user.email}[/] already exists"
        else:
            self.detail = str(self)
        self.status_code = status.HTTP_400_BAD_REQUEST


class UserNotExists(FastAPIUsersException):
    def __init__(self, user: str = None) -> None:
        self.detail = f"User {user} не существует"
        self.status_code = status.HTTP_404_NOT_FOUND


class GroupNotExists(FastAPIUsersException):
    def __init__(self, group: str) -> None:
        self.detail = f"Группа <{group}> не существует"
        self.status_code = status.HTTP_404_NOT_FOUND


class UserInactive(FastAPIUsersException):
    def __init__(self, user: UserScheme | None = None) -> None:
        if user:
            # detail = ErrorCode.LOGIN_USER_NOT_VERIFIED,
            self.detail = f"User {user.username} inactive"
        else:
            self.detail = str(self)
        self.status_code = status.HTTP_400_BAD_REQUEST


class UserAlreadyVerified(FastAPIUsersException):
    def __init__(self, user: UserScheme | None = None) -> None:
        if user:
            self.detail = f"User [cyan b]{user.username}[/] already verified"
        else:
            self.detail = str(self)
        self.status_code = status.HTTP_400_BAD_REQUEST


class InvalidVerifyToken(FastAPIUsersException):
    def __init__(self, msg: Exception | str | None = None) -> None:
        # log.debug(msg)
        self.detail = f"Токен не валиден: {msg}"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class InvalidResetPasswordToken(FastAPIUsersException):
    def __init__(self, msg: Exception | str | None = None) -> None:
        self.detail = f"Токен не валиден: {msg}"
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class InvalidCredentials(FastAPIUsersException):
    def __init__(self, msg: Exception | str | None = None) -> None:
        self.detail = f"Пользователь {msg} не существует или пароль не подходит."
        self.status_code = status.HTTP_400_BAD_REQUEST
