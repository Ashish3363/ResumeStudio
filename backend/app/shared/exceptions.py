# App exception types + handlers.

"""
app/shared/exceptions.py
========================

Typed application errors + the FastAPI handler that renders them.

Why a custom hierarchy instead of raising fastapi.HTTPException everywhere?
- Service and repository code stays free of web-framework details. It raises a
  *business* concept ("invalid credentials"), and the web layer decides how
  that becomes an HTTP response. This matches the project's rule that each
  module is independently maintainable.
- Every error carries a machine-readable `code`, so the frontend can branch on
  `code == "email_exists"` instead of pattern-matching human text.

How it works:
- All app errors subclass `AppError`, which holds an HTTP `status_code`, a
  stable `code`, and a human-readable `detail`.
- `register_exception_handlers(app)` (called once from main.py) registers a
  single handler that converts any raised `AppError` into a JSONResponse of
  the form: {"detail": "...", "code": "..."} with the right status code.

Anything that raises one of these can be anywhere in the call stack — the
handler catches it at the framework boundary.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for all handled application errors.

    Subclasses set class-level `status_code`, `code`, and `detail`. Callers may
    override the message per-instance: `raise InvalidToken("Missing token.")`.

    Attributes:
        status_code: HTTP status the handler will respond with.
        code:        Stable, machine-readable error identifier for the client.
        detail:      Human-readable explanation (safe to show to the user).
    """

    status_code: int = 400
    code: str = "app_error"
    detail: str = "Something went wrong."

    def __init__(self, detail: str | None = None):
        # Allow an optional custom message while keeping the class default.
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class InvalidCredentials(AppError):
    """Login failed. Deliberately generic so it can't be used to probe which
    emails exist (returned for both 'no such user' and 'wrong password')."""

    status_code = 401
    code = "invalid_credentials"
    detail = "Incorrect email or password."


class InvalidToken(AppError):
    """A JWT was missing, malformed, expired, of the wrong type, or its `ver`
    no longer matches users.token_version (i.e. it was revoked)."""

    status_code = 401
    code = "invalid_token"
    detail = "Invalid or expired token."


class EmailAlreadyExists(AppError):
    """Registration attempted with an email that's already taken."""

    status_code = 409
    code = "email_exists"
    detail = "An account with this email already exists."


class NotFoundError(AppError):
    """A requested resource does not exist (or isn't visible to this user)."""

    status_code = 404
    code = "not_found"
    detail = "Resource not found."


def register_exception_handlers(app: FastAPI) -> None:
    """Wire the AppError handler into the FastAPI app.

    Call this once during app setup (in main.py, right after the app is
    created). After this, any `AppError` raised anywhere while handling a
    request is converted to a structured JSON response instead of surfacing
    as an unhandled 500.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.code},
        )
