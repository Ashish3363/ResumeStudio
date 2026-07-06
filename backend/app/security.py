# Password hashing (bcrypt/argon2) + JWT issue/verify + token_version check.

"""
app/security.py
===============

Cryptographic primitives for authentication. This module is intentionally
*pure*: it knows nothing about the database, request objects, or FastAPI. It
only turns values in → values out, so it can be unit-tested in isolation and
imported from anywhere without side effects.

It provides two things:

1. Password hashing
   - `hash_password`   : plaintext -> bcrypt hash (store this in the DB)
   - `verify_password` : plaintext + stored hash -> bool (login check)

2. JSON Web Tokens (JWT)
   - `create_access_token`  : short-lived token sent on every request
   - `create_refresh_token` : long-lived token used only to mint new access tokens
   - `decode_token`         : verify signature + expiry, return the claims

Token design
------------
Every token carries three custom claims in addition to the standard ones:

    sub  : the user's id, as a string (JWT requires `sub` to be a string)
    type : "access" or "refresh" — so an access token can't be replayed as a
           refresh token (and vice-versa)
    ver  : a snapshot of `users.token_version` at issue time

`ver` is the revocation mechanism. On logout (or a forced "log out everywhere")
we increment `users.token_version` in the DB; every token minted before that
carries the old `ver`, so the check `token.ver == user.token_version` fails and
the token is rejected — no server-side token blacklist required.

Standard claims (`iat`, `exp`) are added automatically; `python-jose` verifies
the signature and rejects expired tokens inside `decode_token`.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.config import settings

# --- Token type markers -----------------------------------------------------
# Stored in the "type" claim so we can tell access and refresh tokens apart.
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------
# We use the `bcrypt` package directly rather than passlib: passlib is
# unmaintained (last release 2020) and its bcrypt backend crashes against
# bcrypt >= 4.1, which raises on inputs longer than 72 bytes instead of
# truncating.

def _pw_bytes(plain: str) -> bytes:
    """Encode a password to the bytes bcrypt hashes.

    bcrypt only uses the first 72 *bytes*. Modern bcrypt raises on longer
    input, so we slice to 72 bytes here — matching bcrypt's own semantics and
    keeping hash/verify consistent. (The schema also caps length at 72.)
    """
    return plain.encode("utf-8")[:72]


def hash_password(plain: str) -> str:
    """Hash a plaintext password for storage.

    Args:
        plain: The user's raw password.

    Returns:
        A bcrypt hash string (includes algorithm, cost, and salt) safe to store.
    """
    return bcrypt.hashpw(_pw_bytes(plain), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Check a login attempt against a stored hash.

    Args:
        plain:  The password the user just submitted.
        hashed: The bcrypt hash previously produced by `hash_password`.

    Returns:
        True if the password matches, False otherwise. Never raises on a
        mismatch or a malformed stored hash — a wrong password is a normal,
        expected outcome.
    """
    try:
        return bcrypt.checkpw(_pw_bytes(plain), hashed.encode("utf-8"))
    except ValueError:
        # Malformed/`unknown-format stored hash — treat as a failed match.
        return False


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
def _create_token(subject: str, token_version: int, token_type: str, ttl: timedelta) -> str:
    """Build and sign a JWT. Internal helper for the two public token makers.

    Args:
        subject:       Value for the `sub` claim — the user id as a string.
        token_version: Current `users.token_version`, embedded as `ver`.
        token_type:    TOKEN_TYPE_ACCESS or TOKEN_TYPE_REFRESH.
        ttl:           How long the token stays valid (sets the `exp` claim).

    Returns:
        The encoded, signed JWT string.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "ver": token_version,
        "iat": now,             # issued-at
        "exp": now + ttl,       # expiry — python-jose enforces this on decode
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str, token_version: int) -> str:
    """Mint a short-lived access token (TTL from settings.JWT_ACCESS_TTL_MIN).

    Sent by the client on every protected request in the
    `Authorization: Bearer <token>` header.
    """
    return _create_token(
        subject,
        token_version,
        TOKEN_TYPE_ACCESS,
        timedelta(minutes=settings.JWT_ACCESS_TTL_MIN),
    )


def create_refresh_token(subject: str, token_version: int) -> str:
    """Mint a long-lived refresh token (TTL from settings.JWT_REFRESH_TTL_DAYS).

    Used ONLY against the /refresh endpoint to obtain a fresh access token,
    so the user doesn't have to log in again every few minutes.
    """
    return _create_token(
        subject,
        token_version,
        TOKEN_TYPE_REFRESH,
        timedelta(days=settings.JWT_REFRESH_TTL_DAYS),
    )


def decode_token(token: str) -> dict:
    """Verify a token's signature + expiry and return its claims.

    Args:
        token: The raw JWT string from the client.

    Returns:
        The decoded claims dict (contains `sub`, `type`, `ver`, `iat`, `exp`).

    Raises:
        jose.JWTError: if the signature is invalid, the token is malformed, or
            it has expired. Callers (service / dependency layer) catch this and
            translate it into a 401 via the InvalidToken app exception.
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
