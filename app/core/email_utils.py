import os
import aiosmtplib
from email.message import EmailMessage

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


async def send_email(to: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    await aiosmtplib.send(
        msg,
        hostname=EMAIL_HOST,
        port=EMAIL_PORT,
        start_tls=True,
        username=EMAIL_USER,
        password=EMAIL_PASS
    )
