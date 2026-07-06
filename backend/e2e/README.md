# Backend E2E API Tests (Playwright)

End-to-end tests that exercise the ResumeStudio backend over **real HTTP**. They
use Playwright's API-testing `request` fixture (no browser) to call the running
FastAPI app exactly as a client would.

Currently covers the **JWT auth slice** (`/api/auth/*`).

---

## How it works

- **Isolated database.** Tests never touch the dev DB. Playwright's
  `globalSetup` runs [`../scripts/init_test_db.py`](../scripts/init_test_db.py),
  which creates a dedicated `resumeStudio_test` database (if missing), builds the
  schema from `Base.metadata`, and truncates all tables for a clean slate.
- **Self-managed server.** Playwright's `webServer` starts `uvicorn` itself,
  bound to the test DB via a `DATABASE_URL` env override. It waits for
  `GET /health` before running tests and shuts the server down afterward.
- **Independent tests.** Each test registers a **freshly-generated unique email**,
  so tests don't collide and need no per-test cleanup. They run serially
  (`workers: 1`) for predictable shared-DB state.

```
Playwright  ──globalSetup──▶  init_test_db.py   (create/reset resumeStudio_test)
            ──webServer────▶  uvicorn app.main:app  (DATABASE_URL → test DB)
            ──request──────▶  http://127.0.0.1:8000/api/auth/*
```

---

## Prerequisites

1. **PostgreSQL running** locally on `localhost:5432` with the credentials in
   `playwright.config.ts` (`postgres:root`). The test DB is created automatically.
2. **Backend venv** at `backend/.venv` with deps installed
   (`pip install -r ../requirements.txt`). The config invokes
   `../.venv/Scripts/python.exe`.
3. **Node dependencies** installed here:
   ```bash
   npm install
   ```
   (Only `@playwright/test` — no browser download is needed for API tests.)

> Stop any server you have running on port `8000` before running the suite —
> Playwright starts its own (test-DB) server and will not reuse an existing one.

---

## Running

```bash
cd backend/e2e
npm test              # or: npx playwright test
```

Useful variants:

```bash
npx playwright test --reporter=list        # concise per-test output (default here)
npx playwright test auth.spec.ts -g "logout"  # run a single test by name
npx playwright test --reporter=html        # rich HTML report -> playwright-report/
```

---

## Files

| File | Purpose |
|---|---|
| `playwright.config.ts` | Test dir, base URL, and the `webServer` (uvicorn) + test-DB wiring. |
| `global-setup.ts` | Runs `scripts/init_test_db.py` once before the suite. |
| `tests/auth.spec.ts` | The auth API tests (below). |
| `../scripts/init_test_db.py` | Creates + resets the `resumeStudio_test` database. |

---

## Test coverage — `tests/auth.spec.ts`

| # | Test | Asserts |
|---|---|---|
| 1 | register returns a safe user view (201) | 201; body has `id/email/plan/is_email_verified`; **never** `password_hash` or `token_version`. |
| 2 | duplicate email rejected | 409 with `code: "email_exists"`. |
| 3 | too-short password rejected | 422 (Pydantic validation, `min_length=8`). |
| 4 | login returns token pair | 200; non-empty `access_token` + `refresh_token`; `token_type: "bearer"`. |
| 5 | login wrong password | 401 with `code: "invalid_credentials"`. |
| 6 | login unknown email | 401 `invalid_credentials` (same error as wrong password → no user enumeration). |
| 7 | `/me` without token | 401 with `code: "invalid_token"`. |
| 8 | `/me` with valid access token | 200; returns the caller's email. |
| 9 | refresh issues working tokens | 200; the new access token authenticates `/me`. |
| 10 | access token used as refresh | 401 `invalid_token` (token-type check). |
| 11 | garbage bearer token | 401 `invalid_token` (bad signature/format). |
| 12 | logout revokes tokens | logout 204; the old access token **and** refresh token are then rejected (401) via the bumped `token_version`. |

All 12 currently pass.

---

## Adding tests for future slices

Add a new `tests/<feature>.spec.ts`. To hit protected routes, register + log in a
user (see the `registerAndLogin` helper in `auth.spec.ts`) and pass
`Authorization: Bearer <access_token>`. The test DB is reset once per run in
`globalSetup`; keep tests independent by generating unique inputs per test.
