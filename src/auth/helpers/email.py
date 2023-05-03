from pathlib import Path

from fastapi import Request
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.schemas.request import EmailSchema

mail_conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD.get_secret_value(),
    MAIL_FROM=config.MAIL_SENDER,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    SUPPRESS_SEND=config.SUPPRESS_SEND,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "html_templates",
)

mail = FastMail(mail_conf)


async def send_verification_email(email: EmailSchema, request: Request = None) -> None:
    """Send user verification email"""
    # Change this later to public endpoint
    url = f"{config.ROOT_API_URL}{config.VERIFICATION_URL}/{email.body['token']}"
    # log.debug(mail_conf)
    if config.MAIL_CONSOLE or config.TESTING:
        ...
        # log.info(email)
    email.body["url"] = url
    message = MessageSchema(
        recipients=email.email,
        subject="Auth-v2, подтвердите email",
        template_body=email.body,
        subtype="html",
    )
    await mail.send_message(message, template_name="verify_email.html")


async def send_password_reset_email(email: EmailSchema, request: Request = None) -> None:
    """Отсылает письмо со ссылкой на сброс пароля"""
    # Change this later to public endpoint
    url = f"{config.ROOT_API_URL}{config.PASSWORD_RESET_URL}"
    if config.MAIL_CONSOLE or config.TESTING:
        log.info(email)
    email.body["url"] = url
    message = MessageSchema(
        recipients=email.email,
        subject="Auth-v2, ссылка для сброса пароля",
        template_body=email.body,
        subtype="html",
    )
    await mail.send_message(message, template_name="reset_password.html")


async def write_response(token: str, temp_file: str = "temp.txt") -> None:
    """пишет токен во временный файл на диске, исп-ся в тестах"""
    if config.MAIL_CONSOLE or config.TESTING:
        with open(temp_file, "w", encoding="utf-8") as fp:
            fp.write(token)
