import os
import smtplib
import logging
from email.message import EmailMessage
from fastapi import BackgroundTasks

logger = logging.getLogger(__name__)

# Default config for SMTP/Resend
SMTP_SERVER = os.getenv("SMTP_SERVER", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "chorespec@example.com")


def send_email_sync(to_email: str, subject: str, body: str):
    """
    Synchronously sends an email.
    If SMTP_SERVER is not configured, logs to stdout as a fallback.
    """
    if not SMTP_SERVER:
        logger.info(
            f"[MOCK EMAIL] To: {to_email} | Subject: {subject} | Body: {body}")
        return

    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = DEFAULT_FROM_EMAIL
        msg['To'] = to_email

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()

        if SMTP_USERNAME and SMTP_PASSWORD:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)

        server.send_message(msg)
        server.quit()
        logger.info(f"Successfully sent email to {to_email}")

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")


def send_email_background(background_tasks: BackgroundTasks, to_email: str, subject: str, body: str):
    """
    Queue an email to be sent in the background.
    """
    if not to_email:
        return

    background_tasks.add_task(send_email_sync, to_email, subject, body)
