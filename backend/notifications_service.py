import os
import smtplib
import logging
import json
from email.message import EmailMessage
from fastapi import BackgroundTasks
from .database import SessionLocal
from . import crud

try:
    from pywebpush import webpush, WebPushException
except ImportError:
    webpush = None
    WebPushException = Exception

logger = logging.getLogger(__name__)

# Default config for SMTP/Resend
SMTP_SERVER = os.getenv("SMTP_SERVER", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "chorespec@example.com")

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_CLAIMS_EMAIL = os.getenv("VAPID_CLAIMS_EMAIL", "mailto:admin@example.com")


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


def send_push_sync(subscription_info: dict, payload: dict):
    if not webpush:
        logger.error("pywebpush not installed. Cannot send push.")
        return

    if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
        logger.info(f"[MOCK PUSH] To: {subscription_info.get('endpoint')} | Payload: {payload}")
        return

    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_CLAIMS_EMAIL}
        )
        logger.info(f"Successfully sent push notification to {subscription_info.get('endpoint')}")
    except WebPushException as ex:
        logger.error(f"Failed to send push: {ex}")
        if ex.response and ex.response.status_code == 410:
            logger.info("Subscription expired/removed. Should delete from DB.")
            # In a production app, we would remove the sub from the DB here


def send_push_to_user_sync(user_id: int, title: str, message: str, data: dict = None):
    db = SessionLocal()
    try:
        subs = crud.get_push_subscriptions_by_user(db, user_id)
        if not subs:
            return

        payload = {
            "title": title,
            "body": message,
            "data": data or {}
        }
        for sub in subs:
            sub_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "auth": sub.auth,
                    "p256dh": sub.p256dh
                }
            }
            send_push_sync(sub_info, payload)
    finally:
        db.close()


def send_push_to_user_background(
    background_tasks: BackgroundTasks, user_id: int, title: str, message: str, data: dict = None
):
    """Queue a push notification to all devices for a user."""
    background_tasks.add_task(send_push_to_user_sync, user_id, title, message, data)
