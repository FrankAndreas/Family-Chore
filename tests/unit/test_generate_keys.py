import base64

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from py_vapid import Vapid

from backend.generate_keys import generate_env_lines


def test_generate_keys_outputs_usable_env_lines():
    env = dict(line.split("=", 1) for line in generate_env_lines())

    # No JWT secret any more: the login is the family hub's (spec 2026-10-30)
    assert set(env) == {"VAPID_PRIVATE_KEY", "VAPID_PUBLIC_KEY"}

    # pywebpush loads a non-file private key via Vapid.from_string
    vapid = Vapid.from_string(env["VAPID_PRIVATE_KEY"])
    public_raw = vapid.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    assert base64.urlsafe_b64encode(public_raw).decode().rstrip("=") == env["VAPID_PUBLIC_KEY"]


def test_generate_keys_are_random():
    assert generate_env_lines() != generate_env_lines()
