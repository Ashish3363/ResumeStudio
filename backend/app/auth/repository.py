# Auth DB queries: fetch user by email, create user, bump users.token_version (revoke refresh).

"""
app/auth/repository.py
======================

Data-access layer for authentication. This is the single place that knows how
to query and mutate `users` rows for auth purposes; everything above it (the
service) works through these functions instead of writing SQL/ORM queries
directly. That keeps DB concerns in one file and the service readable.

Transaction boundaries:
    These functions never call `commit()`. They only stage work (`add`/`flush`).
    The *service* owns the transaction and commits once the whole operation has
    succeeded. `flush()` pushes pending SQL to the database — enough to obtain a
    generated primary key — without ending the transaction, so the caller can
    still roll back on a later failure.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    """Look up a user by their email address.

    Args:
        db:    The active session.
        email: Email to search for (must match exactly; emails are stored
               as-entered and the column is UNIQUE).

    Returns:
        The matching `User`, or None if no account has that email.
    """
    return db.scalar(select(User).where(User.email == email))


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    """Load a user by primary key.

    Used by token verification (`get_current_user`, refresh) to resolve the
    `sub` claim back into a live User row.

    Args:
        db:      The active session.
        user_id: The user's UUID.

    Returns:
        The `User`, or None if the id doesn't exist. `Session.get` checks the
        identity map first, so repeated lookups in one request are cheap.
    """
    return db.get(User, user_id)


def create_user(
    db: Session,
    *,
    email: str,
    password_hash: str,
    full_name: str | None,
) -> User:
    """Stage a new user row and return the (not-yet-committed) instance.

    The password is expected to be ALREADY HASHED — this layer never sees or
    hashes plaintext; that happens in the service via `security.hash_password`.

    Args:
        db:            The active session.
        email:         New account's email (uniqueness is enforced by the DB;
                       the service checks first for a friendly error).
        password_hash: bcrypt hash produced by the security module.
        full_name:     Optional display name.

    Returns:
        The `User` after `flush()`, so `user.id` and DB defaults
        (`token_version`, `plan`, timestamps) are populated. The service must
        `commit()` to persist it.
    """
    user = User(email=email, password_hash=password_hash, full_name=full_name)
    db.add(user)
    db.flush()  # emit INSERT now so the generated id + server defaults are available
    return user


def bump_token_version(db: Session, user: User) -> None:
    """Increment the user's `token_version`, revoking all outstanding tokens.

    Every access/refresh token embeds the `token_version` it was minted with.
    Bumping it here means every previously-issued token now carries a stale
    `ver` and will fail verification. This is how logout (and "log out
    everywhere") works without a server-side token blacklist.

    Args:
        db:   The active session.
        user: The user whose tokens should be invalidated.
    """
    user.token_version += 1
    db.flush()
