import os
import smtplib
import logging
import json
import base64
from pathlib import Path
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

VAPID_CLAIMS_EMAIL = os.getenv("VAPID_CLAIMS_EMAIL", "mailto:admin@example.com")

# Resolve the backend directory (where .env and private_key.pem live)
_BACKEND_DIR = Path(__file__).resolve().parent
_PEM_PATH = _BACKEND_DIR / "private_key.pem"
_ENV_PATH = _BACKEND_DIR / ".env"


def _generate_vapid_keys() -> tuple[str, str]:
    """Generate a new VAPID key pair, save the PEM, and return (pem_path, public_key)."""
    try:
        from py_vapid import Vapid
        from cryptography.hazmat.primitives.serialization import Encoding
        from cryptography.hazmat.primitives.serialization import PublicFormat
    except ImportError:
        logger.error("py_vapid / cryptography not installed. Cannot generate VAPID keys.")
        return "", ""

    v = Vapid()
    v.generate_keys()

    # Write private key PEM
    pem_bytes = v.private_pem()
    _PEM_PATH.write_bytes(pem_bytes)
    logger.info(f"Generated new VAPID private key at {_PEM_PATH}")

    # Derive the applicationServerKey (URL-safe base64, unpadded)
    raw_pub = v.public_key.public_bytes(
        encoding=Encoding.X962,
        format=PublicFormat.UncompressedPoint,
    )
    app_server_key = base64.urlsafe_b64encode(raw_pub).decode().rstrip("=")

    # Persist to .env so the keys survive restarts
    env_lines = []
    if _ENV_PATH.exists():
        env_lines = _ENV_PATH.read_text().splitlines()

    # Remove old VAPID entries if present
    env_lines = [
        ln for ln in env_lines
        if not ln.startswith("VAPID_PRIVATE_KEY=") and not ln.startswith("VAPID_PUBLIC_KEY=")
    ]
    env_lines.append(f"VAPID_PRIVATE_KEY={_PEM_PATH}")
    env_lines.append(f"VAPID_PUBLIC_KEY={app_server_key}")
    _ENV_PATH.write_text("\n".join(env_lines) + "\n")
    logger.info("VAPID keys written to .env")

    return str(_PEM_PATH), app_server_key


def _load_vapid_keys() -> tuple[str, str]:
    """Load VAPID keys from env vars, or auto-generate if missing."""
    private_key = os.getenv("VAPID_PRIVATE_KEY", "")
    public_key = os.getenv("VAPID_PUBLIC_KEY", "")

    if private_key and public_key:
        return private_key, public_key

    # Check if a PEM file already exists on disk (env just not loaded)
    if _PEM_PATH.exists() and not private_key:
        logger.warning(
            f"VAPID_PRIVATE_KEY env var not set, but {_PEM_PATH} exists. "
            "Set VAPID_PRIVATE_KEY and VAPID_PUBLIC_KEY in your environment."
        )
        return str(_PEM_PATH), public_key

    # Nothing configured — auto-generate
    logger.info("No VAPID keys configured. Auto-generating a new key pair...")
    return _generate_vapid_keys()


VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY = _load_vapid_keys()


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
