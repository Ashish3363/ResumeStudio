# Auth FastAPI dependencies: get_current_user (decode JWT, verify token_version, load User).
# Other features import this via `from app.auth.dependencies import get_current_user`.

"""
app/auth/dependencies.py
========================

FastAPI dependency that authenticates a request and resolves the current user.

`get_current_user` is the single gate every protected endpoint goes through.
Adding it (via the `CurrentUser` alias) to a route signature makes that route
require a valid access token; without one, the request is rejected with 401
before the handler runs.

Verification steps (each failure -> InvalidToken -> 401):
    1. A bearer token is actually present.
    2. Its signature + expiry are valid (delegated to security.decode_token).
    3. Its `type` claim is "access" — a refresh token cannot be replayed here.
    4. Its `sub` parses to a real user id and that user still exists.
    5. Its embedded `ver` matches users.token_version — i.e. not revoked by a
       logout. (This is why access tokens are checked against the DB every
       request: it buys instant revocation, at the cost of one indexed lookup
       we'd be doing anyway to load the user.)

Other features import `get_current_user` from here to protect their own routes.
"""

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.auth import repository
from app.database import SessionDep
from app.security import TOKEN_TYPE_ACCESS, decode_token
from app.shared.exceptions import InvalidToken
from app.users.models import User

# auto_error=False: when the header is missing we raise our OWN InvalidToken
# (uniform 401 JSON via the app error handler) instead of FastAPI's default 403.
_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    db: SessionDep,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None,
) -> User:
    """Resolve the authenticated user from the request's bearer token.

    Args:
        db:    Injected DB session (from get_db).
        creds: Parsed Authorization header, or None if absent.

    Returns:
        The authenticated `User`.

    Raises:
        InvalidToken: if the token is missing, malformed, expired, of the wrong
            type, points to a non-existent user, or has been revoked.
    """
    if creds is None:
        raise InvalidToken("Missing bearer token.")

    try:
        payload = decode_token(creds.credentials)
    except JWTError:
        raise InvalidToken()

    # Reject a refresh token used where an access token is required.
    if payload.get("type") != TOKEN_TYPE_ACCESS:
        raise InvalidToken()

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        raise InvalidToken()

    user = repository.get_user_by_id(db, user_id)
    # Revocation check: a stale `ver` means the token was invalidated by logout.
    if user is None or payload.get("ver") != user.token_version:
        raise InvalidToken()

    return user


# Convenience alias so routes can write `current_user: CurrentUser` and get an
# authenticated User injected — reads cleanly and hides the Depends wiring.
CurrentUser = Annotated[User, Depends(get_current_user)]
