import secrets

from ooklept.stores import stores

CSRF_SESSION_KEY = "_csrf_token"
CSRF_FIELD_NAME = "_csrf_token"
CSRF_EXEMPT_CONTENT_TYPES = {"application/json"}
CSRF_EXEMPT_PATHS = set()  # e.g. {"webhooks/stripe.py"} for routes that legitimately receive third-party POSTs


def get_or_create_csrf_token() -> str:
    """
    Returns this session's CSRF token, generating one on first use.
    One token per session — persists across pages until the session
    ends or rotates.
    """
    existing = stores.session_store.get(CSRF_SESSION_KEY)
    if existing:
        return existing
    token = secrets.token_urlsafe(32)
    stores.session_store.set(CSRF_SESSION_KEY, token)
    return token


def verify_csrf_token(submitted: str | None) -> bool:
    expected = stores.session_store.get(CSRF_SESSION_KEY)
    if not expected or not submitted:
        return False
    return secrets.compare_digest(submitted, expected)
