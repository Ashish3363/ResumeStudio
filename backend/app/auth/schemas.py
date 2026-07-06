# Auth DTOs: register/login requests, token responses.

"""
app/auth/schemas.py
===================

Request/response data contracts for the auth endpoints. These are pure Pydantic
models — no DB access, no business logic. FastAPI uses them to:

  - validate + parse incoming JSON  (RegisterRequest, LoginRequest, RefreshRequest)
  - serialize outgoing JSON         (TokenResponse, UserOut)

Output-safety note:
    `UserOut` is the ONLY representation of a User sent to clients. Because it
    lists fields explicitly, sensitive columns (`password_hash`, `token_version`)
    are structurally impossible to leak — they simply aren't part of the shape.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Body for POST /api/auth/register."""

    email: EmailStr  # validated as a real email; also requires the email-validator package
    # min 8 for basic strength; max 72 because bcrypt only hashes the first 72
    # *bytes* — rejecting longer input here prevents a silently-ignored tail.
    password: str = Field(min_length=8, max_length=72)
    full_name: str | None = None


class LoginRequest(BaseModel):
    """Body for POST /api/auth/login.

    Intentionally no length/format rules on `password` beyond it being a string:
    validation belongs on registration, and the login form shouldn't advertise
    the password policy.
    """

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Body for POST /api/auth/refresh — the client's stored refresh token."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Response for /login and /refresh: a fresh access + refresh pair.

    `token_type` is "bearer", i.e. the client sends the access token as
    `Authorization: Bearer <access_token>`.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    """Public, safe view of a user. Returned by /register and /me.

    `from_attributes=True` lets us build this directly from the SQLAlchemy User
    ORM object: `UserOut.model_validate(user)`.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    plan: str
    is_email_verified: bool
