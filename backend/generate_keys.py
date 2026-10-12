"""Print a JWT secret and a VAPID key pair as .env lines.

Usage (no database or other settings needed):
    python -m backend.generate_keys
"""
import base64
import secrets

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from py_vapid import Vapid


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def generate_env_lines() -> list[str]:
    vapid = Vapid()
    vapid.generate_keys()
    # Raw 32-byte private scalar: a single-line value pywebpush loads via Vapid.from_string
    private_raw = vapid.private_key.private_numbers().private_value.to_bytes(32, "big")
    public_raw = vapid.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    return [
        f"JWT_SECRET_KEY={secrets.token_hex(32)}",
        f"VAPID_PRIVATE_KEY={_b64url(private_raw)}",
        f"VAPID_PUBLIC_KEY={_b64url(public_raw)}",
    ]


if __name__ == "__main__":
    print("\n".join(generate_env_lines()))
