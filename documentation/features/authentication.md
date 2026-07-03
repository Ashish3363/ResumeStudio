# Authentication

**Scope:** MVP

## Summary
Email + password authentication with **JWT access tokens** and **refresh tokens**
(rotation + revocation). Roll-your-own (no managed auth provider).

## Stored per account
Career profile (master data), saved resumes (up to 10), job descriptions, generated PDFs,
subscription status.

## Tokens
- **Access token** — short-lived, stateless JWT, sent on each API request.
- **Refresh token** — long-lived JWT that embeds a `token_version` claim. On refresh,
  the claim is validated against `users.token_version`.
- **Revocation** — incrementing `users.token_version` invalidates **all** outstanding
  refresh tokens for that user (logout-everywhere, password change). No token rows are
  stored (no `refresh_tokens` table).

> Tradeoff accepted: this gives coarse, all-sessions revocation and keeps the schema at
> 4 tables. Per-device revocation and refresh-token reuse-detection are deferred; if needed
> later, reintroduce a `refresh_tokens` table without other schema changes.

## Passwords
Hashed with bcrypt or argon2. Plaintext never stored or logged.

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/register` | create account |
| POST | `/login` | issue access + refresh tokens |
| POST | `/refresh` | validate `token_version`, issue new access token |
| POST | `/logout` | bump `users.token_version` (revokes all sessions) |

A FastAPI `get_current_user` dependency guards all protected routes.

## Verification checklist
register → login → access protected route → refresh (new access token works) → bump
`token_version` → prior refresh token rejected.

## Deferred (Phase 2)
Email verification, password reset, social login.
