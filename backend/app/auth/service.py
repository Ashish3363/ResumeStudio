# Auth logic: credential checks; token issue/rotate via token_version.

"""
app/auth/service.py
===================

Business logic for authentication. This layer sits between the HTTP router
(above) and the repository + security modules (below). It owns:

- The *rules*: email uniqueness on register, credential checking on login,
  token-type + revocation checks on refresh.
- The *transaction*: repository functions only stage work; the service decides
  when the unit of work is complete and calls `commit()`.
- The *translation* of failure into typed app errors (InvalidCredentials,
  EmailAlreadyExists, InvalidToken) — never HTTP details, so this stays
  framework-agnostic.

It knows nothing about FastAPI/requests; the router adapts these functions to
HTTP.

Revocation model (recap):
    Every token embeds `ver` = the user's token_version at issue time. A token
    is valid only while `token.ver == user.token_version`. Logout bumps the
    version, instantly invalidating every outstanding token for that user.
"""

import uuid

from jose import JWTError
from sqlalchemy.orm import Session

from app import security
from app.auth import repository
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.security import TOKEN_TYPE_REFRESH
from app.shared.exceptions import (
    EmailAlreadyExists,
    InvalidCredentials,
    InvalidToken,
)
from app.users.models import User


def _issue_tokens(user: User) -> TokenResponse:
    """Mint a fresh access + refresh pair for a user.

    Both tokens embed the user's current `token_version`, so they stay valid
    only until the next logout/revocation.

    Args:
        user: The authenticated user.

    Returns:
        A TokenResponse carrying both tokens (bearer type).
    """
    subject = str(user.id)  # JWT `sub` must be a string
    return TokenResponse(
        access_token=security.create_access_token(subject, user.token_version),
        refresh_token=security.create_refresh_token(subject, user.token_version),
    )


def register(db: Session, data: RegisterRequest) -> User:
    """Create a new account.

    Steps: reject a duplicate email, hash the password, stage the row, commit.

    Args:
        db:   Active session (the service commits it).
        data: Validated registration payload.

    Returns:
        The persisted `User`.

    Raises:
        EmailAlreadyExists: if the email is already registered.
    """
    if repository.get_user_by_email(db, data.email):
        raise EmailAlreadyExists()

    user = repository.create_user(
        db,
        email=data.email,
        password_hash=security.hash_password(data.password),
        full_name=data.full_name,
    )
    db.commit()        # end the transaction; the row is now durable
    db.refresh(user)   # reload DB-side defaults (timestamps, plan, ...)
    return user


def login(db: Session, data: LoginRequest) -> TokenResponse:
    """Verify credentials and issue a token pair.

    Uses one and the same error for "no such email" and "wrong password" so an
    attacker can't use login responses to discover which emails are registered.

    Args:
        db:   Active session.
        data: Validated login payload.

    Returns:
        A fresh access + refresh token pair.

    Raises:
        InvalidCredentials: if the email is unknown or the password is wrong.
    """
    user = repository.get_user_by_email(db, data.email)
    if user is None or not security.verify_password(data.password, user.password_hash):
        raise InvalidCredentials()
    return _issue_tokens(user)


def refresh(db: Session, refresh_token: str) -> TokenResponse:
    """Exchange a valid refresh token for a new access + refresh pair.

    Validation performed, in order:
      1. Signature + expiry (via `decode_token`; JWTError -> InvalidToken).
      2. Token is actually a *refresh* token, not an access token.
      3. `sub` parses to a real user id.
      4. The embedded `ver` still matches the user's current token_version
         (i.e. the token hasn't been revoked by a logout).

    Args:
        db:            Active session.
        refresh_token: The raw refresh JWT from the client.

    Returns:
        A newly-minted token pair.

    Raises:
        InvalidToken: on any of the failures above.
    """
    try:
        payload = security.decode_token(refresh_token)
    except JWTError:
        raise InvalidToken()

    if payload.get("type") != TOKEN_TYPE_REFRESH:
        raise InvalidToken()

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        raise InvalidToken()

    user = repository.get_user_by_id(db, user_id)
    if user is None or payload.get("ver") != user.token_version:
        raise InvalidToken()

    return _issue_tokens(user)


def logout(db: Session, user: User) -> None:
    """Log the user out everywhere by revoking all their tokens.

    Bumps `token_version`, so every access + refresh token issued before now
    fails its `ver` check. There's no per-token blacklist to maintain.

    Args:
        db:   Active session (the service commits it).
        user: The currently-authenticated user (resolved by get_current_user).
    """
    repository.bump_token_version(db, user)
    db.commit()
