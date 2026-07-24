import hashlib
import hmac
import os
import secrets

# TODO
# In production, load this from an env var / secrets manager, not generated at random each boot
# (a random secret each restart would silently invalidate all existing sessions, which is fine
# for security but you may want persistence across restarts).
SECRET_KEY = os.environ.get("OOKLEPT_SECRET_KEY", secrets.token_hex(32)).encode()


def sign_session_id(session_id: str) -> str:
    sig = hmac.new(SECRET_KEY, session_id.encode(), hashlib.sha256).hexdigest()
    return f"{session_id}.{sig}"


def verify_session_cookie(cookie_value: str) -> str | None:
    """Returns the session_id if valid, else None."""
    try:
        session_id, sig = cookie_value.rsplit(".", 1)
    except ValueError:
        return None

    expected_sig = hmac.new(SECRET_KEY, session_id.encode(), hashlib.sha256).hexdigest()

    # constant-time comparison — prevents timing attacks on the signature check
    if hmac.compare_digest(sig, expected_sig):
        return session_id
    return None
