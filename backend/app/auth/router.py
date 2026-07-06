# Auth endpoints: register, login, refresh, logout.

"""
app/auth/router.py
==================

HTTP endpoints for authentication. This is a thin adapter: each handler wires
request/response schemas + dependencies to a `service` call and returns the
result. All rules and side effects live in app.auth.service — routes stay
declarative.

The `router` object is mounted in main.py under the /api/auth prefix, so the
paths below become /api/auth/register, /api/auth/login, etc.

Endpoints
    POST /register  create an account            -> 201 UserOut
    POST /login     exchange credentials for JWTs -> 200 TokenResponse
    POST /refresh   swap a refresh token for JWTs -> 200 TokenResponse
    POST /logout    revoke all of a user's tokens -> 204 (auth required)
    GET  /me        the current user's profile    -> 200 UserOut (auth required)
"""

from fastapi import APIRouter, status

from app.auth import service
from app.auth.dependencies import CurrentUser
from app.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.database import SessionDep

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: SessionDep) -> UserOut:
    """Register a new account and return its public profile.

    A duplicate email is rejected by the service as 409 email_exists. Note this
    does NOT log the user in (no tokens returned) — the client calls /login
    next. (If you'd rather auto-login, switch the response to TokenResponse and
    return service tokens instead.)
    """
    user = service.register(db, data)
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: SessionDep) -> TokenResponse:
    """Authenticate with email + password and receive an access/refresh pair.

    Wrong email or password both yield 401 invalid_credentials (no user
    enumeration).
    """
    return service.login(db, data)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: SessionDep) -> TokenResponse:
    """Exchange a valid, non-revoked refresh token for a new token pair.

    Any problem (expired, wrong type, revoked) yields 401 invalid_token.
    """
    return service.refresh(db, data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: CurrentUser, db: SessionDep) -> None:
    """Log out everywhere by revoking all of the caller's tokens.

    Requires a valid access token (the `CurrentUser` dependency). Bumps the
    user's token_version, so every outstanding access + refresh token stops
    working immediately. Returns 204 No Content.
    """
    service.logout(db, current_user)


@router.get("/me", response_model=UserOut)
def me(current_user: CurrentUser) -> UserOut:
    """Return the authenticated user's public profile.

    Doubles as the smoke test that access-token auth works end to end.
    """
    return UserOut.model_validate(current_user)
