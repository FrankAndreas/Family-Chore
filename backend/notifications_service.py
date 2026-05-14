import smtplib
import logging
import json
import base64
from pathlib import Path
from email.message import EmailMessage
from fastapi import BackgroundTasks
from .database import SessionLocal
from .services import notifications
from .config import settings

try:
    from pywebpush import webpush, WebPushException
except ImportError:
    webpush = None
    WebPushException = Exception

logger = logging.getLogger(__name__)

# Default config for SMTP/Resend
SMTP_SERVER = settings.SMTP_SERVER
SMTP_PORT = settings.SMTP_PORT
SMTP_USERNAME = settings.SMTP_USERNAME
SMTP_PASSWORD = settings.SMTP_PASSWORD
DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL

VAPID_CLAIMS_EMAIL = settings.VAPID_CLAIMS_EMAIL

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
    private_key = settings.VAPID_PRIVATE_KEY
    public_key = settings.VAPID_PUBLIC_KEY

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
    logger.warning(
        "VAPID keys not configured — auto-generating a new key pair. "
        "Set VAPID_PRIVATE_KEY and VAPID_PUBLIC_KEY env vars for production."
    )
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


def send_push_sync(subscription_info: dict, payload: dict) -> bool:
    """Send a push notification. Returns True on success, False on failure.
    Returns None if the subscription is gone (410) so callers can clean up."""
    if not webpush:
        logger.error("pywebpush not installed. Cannot send push.")
        return False

    if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
        logger.info(f"[MOCK PUSH] To: {subscription_info.get('endpoint')} | Payload: {payload}")
        return True

    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_CLAIMS_EMAIL}
        )
        logger.info(f"Successfully sent push notification to {subscription_info.get('endpoint')}")
        return True
    except WebPushException as ex:
        logger.error(f"Failed to send push: {ex}")
        if ex.response and ex.response.status_code == 410:
            return False  # Signal caller to delete this subscription
        return False


def send_push_to_user_sync(user_id: int, title: str, message: str, data: dict = None):
    db = SessionLocal()
    try:
        subs = notifications.get_push_subscriptions_by_user(db, user_id)
        if not subs:
            return

        payload = {
            "title": title,
            "body": message,
            "data": data or {}
        }
        stale_endpoints = []
        for sub in subs:
            sub_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "auth": sub.auth,
                    "p256dh": sub.p256dh
                }
            }
            success = send_push_sync(sub_info, payload)
            if not success:
                stale_endpoints.append(str(sub.endpoint))

        for endpoint in stale_endpoints:
            notifications.delete_push_subscription(db, endpoint)
            logger.info(f"Removed stale push subscription: {endpoint}")
    finally:
        db.close()


def send_push_to_user_background(
    background_tasks: BackgroundTasks, user_id: int, title: str, message: str, data: dict = None
):
    """Queue a push notification to all devices for a user."""
    background_tasks.add_task(send_push_to_user_sync, user_id, title, message, data)
