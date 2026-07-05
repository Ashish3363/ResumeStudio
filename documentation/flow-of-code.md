# Flow of Code — Backend Build Order

A step-by-step order for building the backend from scratch. Written for a first-time
backend build: do the files **top to bottom**. Each phase lists the files, what each
contains, why it comes here, and a **checkpoint** you can actually run before moving on.

## The guiding rule
Build **bottom-up, then in vertical slices**:
1. **Foundation** first (config, DB, base) — nothing runs without it.
2. **Contracts** next (Pydantic schemas) — the shapes every feature passes around.
3. **Features as vertical slices** — each feature = `schema → service → router → wire into main`.
   Build one slice fully and test it before starting the next.

A "vertical slice" means: finish one feature end-to-end (request → logic → response) so you
always have a working app, instead of half-building ten files at once.

Legend: ✅ = **completed** · ▶ = still to write (stub/empty).

---

## Phase 0 — Foundation (get the app to boot)

| Order | File | Contains |
|---|---|---|
| 1 | ✅ `requirements.txt` | Pin the deps you'll import: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `alembic`, `pydantic`, `pydantic-settings`, `psycopg[binary]`, `python-jose[cryptography]`, `passlib[bcrypt]`, `google-generativeai`, `pdfplumber`, `python-docx`, `jinja2`. Then `pip install -r requirements.txt`. |
| 2 | ✅ `app/config.py` | The typed `Settings` + `settings` singleton (env/`.env`). Holds `DATABASE_URL`, JWT settings, `GEMINI_API_KEY`, storage creds, `CORS_ORIGINS`, `SAVED_RESUME_CAP=10`. |
| 3 | ✅ `app/models/base.py` | SQLAlchemy 2.0 declarative `Base` + shared mixins: UUIDv7 primary key, `created_at`/`updated_at`. Every model inherits from these. |
| 4 | ▶ `app/database.py` | The engine (from `settings.DATABASE_URL`), `SessionLocal`, and the `get_db()` FastAPI dependency that yields a session and closes it. |
| 5 | ✅ `app/main.py` | Composition root: create `FastAPI`, add CORS from settings, `lifespan`, `/health`. Routers stay commented until their modules exist. |

**Checkpoint:** `uvicorn app.main:app --reload` boots and `GET /health` → `{"status":"ok"}`.

---

## Phase 1 — Database models (the 4 tables)

Build all four, then generate the first migration. They depend on `models/base.py`.

| Order | File | Contains |
|---|---|---|
| 6 | ✅ `app/models/user.py` | `User`: email (unique), `password_hash`, `is_email_verified`, `profile_picture`, `token_version`, `plan`, timestamps. |
| 7 | ✅ `app/models/career_profile.py` | `CareerProfile`: `user_id` (unique → 1:1), `title`, `profile_json` (JSONB). FK cascade from user. |
| 8 | ✅ `app/models/job_description.py` | `JobDescription`: `user_id`, `company_name`, `job_title`, `jd_text`, `parsed_jd_json` (JSONB). |
| 9 | ✅ `app/models/resume.py` | `Resume`: `user_id`, `job_description_id` (nullable FK), `resume_name`, `resume_json`, `changes_summary`, `pdf_url`, `ats_score`, `overall_match_score`, `match_report`, timestamps. |
| 10 | ✅ `app/models/__init__.py` | Import all models here so Alembic/`Base.metadata` can see them. |

**Then set up migrations:**
| Order | File | Contains |
|---|---|---|
| 11 | ✅ `alembic.ini` + `alembic/env.py` | Point Alembic at `settings.DATABASE_URL` and `Base.metadata` (import from `app.models`). |
| 12 | — | Run `alembic revision --autogenerate -m "initial schema"` then `alembic upgrade head`. |

**Checkpoint:** the 4 tables exist in your Neon/local DB (inspect with any SQL client).

---

## Phase 2 — Schemas (the data contracts)

Pure Pydantic; no DB, no logic. These are the request/response and AI-output shapes.

| Order | File | Contains |
|---|---|---|
| — | ✅ `app/schemas/resume.py` | `ResumeData` + sub-models (skills with `verified`/`level`, experience, etc.). |
| — | ✅ `app/schemas/jd.py` | `JDAnalysis`. |
| 13 | ▶ `app/schemas/matching.py` | `MatchReport`, `MissingSkill`, `SkillVerification`, `VerificationChoice`. |
| 14 | ▶ `app/schemas/auth.py` | Register/login request bodies; token response (`access_token`, `token_type`). |
| 15 | ▶ `app/schemas/profile.py` | Career-profile request/response wrappers around `ResumeData`. |

**Checkpoint:** `python -c "from app.schemas.matching import MatchReport"` imports cleanly.

---

## Phase 3 — Core security (shared by every protected route)

| Order | File | Contains |
|---|---|---|
| 16 | ▶ `app/core/security.py` | Password hash/verify (passlib); JWT create/decode (python-jose); embed `token_version` in the refresh token. |
| 17 | ▶ `app/core/exceptions.py` | App exception types + FastAPI handlers (e.g. 401, 404, quota errors). |
| 18 | ▶ `app/core/deps.py` | `get_current_user()` dependency: read the bearer token, verify it, load the `User` via `get_db`. Depends on security + database + models. |

**Checkpoint:** unit-test `hash → verify` and `create token → decode token` round-trips.

---

## Phase 4 — Auth slice (first full feature)

Do this before other features — everything else needs `get_current_user`.

| Order | File | Contains |
|---|---|---|
| 19 | ▶ `app/auth/service.py` | Logic: create user (hash password), authenticate, issue access+refresh, refresh via `token_version`, logout (bump `token_version`). |
| 20 | ▶ `app/auth/router.py` | `router = APIRouter()` with `POST /register`, `/login`, `/refresh`, `/logout`. Calls the service. |
| 21 | ▶ `app/main.py` (edit) | Uncomment + `include_router(auth_router, prefix="/api/auth")`. |

**Checkpoint:** register → login → call a protected test route → refresh → logout invalidates old refresh.

---

## Phase 5 — AI abstraction (before any AI-using feature)

| Order | File | Contains |
|---|---|---|
| 22 | ▶ `app/ai/provider.py` | The `AIProvider` Protocol: `parse_resume`, `analyze_jd`, `suggest_improvements`, `optimize_content`. Business logic imports **this**, never Gemini directly. |
| 23 | ▶ `app/ai/prompts/` | Prompt templates per task (parse, analyze, suggest, optimize). |
| 24 | ▶ `app/ai/gemini.py` | `GeminiProvider` implementing the Protocol using structured/JSON-schema output bound to the Pydantic schemas. |

**Checkpoint:** call `GeminiProvider().analyze_jd(sample_text)` and get a valid `JDAnalysis`.

---

## Phase 6 — Resume input slice (build the career profile)

| Order | File | Contains |
|---|---|---|
| 25 | ▶ `app/users/service.py` | Get/upsert the user's `career_profiles.profile_json`; merge manual entry. |
| 26 | ▶ `app/users/router.py` | `GET /profile`, `PUT /profile`. Wire into main. |
| 27 | ▶ `app/parser/extractors.py` | PDF (pdfplumber) + DOCX (python-docx) → raw text. |
| 28 | ▶ `app/parser/service.py` | Orchestrate: extract text → `AIProvider.parse_resume` → merge into `profile_json`. |
| 29 | ▶ `app/parser/router.py` | `POST /profile/upload`. Wire into main. |

**Checkpoint:** upload a sample PDF → profile is populated; manual `PUT /profile` also works.

---

## Phase 7 — JD analysis slice

| Order | File | Contains |
|---|---|---|
| 30 | ▶ `app/jd/service.py` | `AIProvider.analyze_jd` → save `JobDescription` row. |
| 31 | ▶ `app/jd/router.py` | `POST /jd/analyze`. Wire into main. |

**Checkpoint:** paste a JD → get + persist a `JDAnalysis`.

---

## Phase 8 — Matching slice (deterministic)

| Order | File | Contains |
|---|---|---|
| 32 | ▶ `app/matching/synonyms.py` | Normalization + synonym map (e.g. `JS`→`JavaScript`). |
| 33 | ▶ `app/matching/service.py` | Deterministic score (weighted set overlap) + diff → `missing_skills`; LLM only for prose suggestions. |
| 34 | ▶ `app/matching/router.py` | `POST /match` → `MatchReport`. Wire into main. |

**Checkpoint:** same profile + JD → identical score across runs (determinism test).

---

## Phase 9 — Generator slice

| Order | File | Contains |
|---|---|---|
| 35 | ▶ `app/generator/service.py` | Apply verifications → `AIProvider.optimize_content`; enforce **verified-skills-only**; return optimized `resume_json` + `changes_summary`. |
| 36 | ▶ `app/generator/router.py` | `POST /generate`. Wire into main. Result is transient until saved. |

**Checkpoint:** JD skill not in profile stays out unless verified; "No Experience" excluded.

---

## Phase 10 — Output pipeline (storage → template → PDF)

Needed before "save with PDF" works.

| Order | File | Contains |
|---|---|---|
| 37 | ▶ `app/storage/service.py` | S3-compatible upload/download/**delete** (delete matters for FIFO eviction). |
| 38 | ▶ `app/template/escaping.py` | Escape LaTeX special chars in every user string. |
| 39 | ▶ `app/template/templates/ats_resume.tex.j2` | The single ATS LaTeX template (layout only; renders `section_order`). |
| 40 | ▶ `app/template/service.py` | `resume_json` → LaTeX via Jinja2 + escaping. |
| 41 | ▶ `app/pdf/service.py` | Tectonic compile: sandbox temp dir, **shell-escape off**, hard timeout → PDF → upload via storage. |

**Checkpoint (highest-risk test):** sample `resume_json` → LaTeX → Tectonic → PDF with **selectable text**; special chars don't break/inject.

---

## Phase 11 — Resumes slice (save / edit / FIFO / download)

| Order | File | Contains |
|---|---|---|
| 42 | ▶ `app/resumes/service.py` | Save (new row → template → PDF → storage), **FIFO cap** using `settings.SAVED_RESUME_CAP` (evict oldest row + its PDF, atomic), edit-in-place, delete, list, get. |
| 43 | ▶ `app/resumes/router.py` | `POST /resumes`, `GET /resumes`, `GET/PATCH/DELETE /resumes/{id}`, `GET /resumes/{id}/pdf`. Wire into main. |

**Checkpoint:** save 11 resumes → oldest row + its PDF removed; edit overwrites in place; download works.

---

## Phase 12 — Subscription scaffolding

| Order | File | Contains |
|---|---|---|
| 44 | ▶ `app/subscription/service.py` | Read `users.plan`; MVP only guards the 10-resume cap (payments deferred to Phase 2). |

---

## Phase 13 — Tests & packaging

| Order | File | Contains |
|---|---|---|
| 45 | ▶ `tests/conftest.py` | Fixtures: test DB session, `TestClient`, an authed-user helper. |
| 46 | ▶ `tests/…` | One test per slice checkpoint above. |
| 47 | ✅ `Dockerfile` · `docker-compose.yml` | Python base + Tectonic; dev stack. Do last, once the app runs locally. **Note:** `Dockerfile` done (multi-stage base→builder→dev/prod, pinned Tectonic); `docker-compose.yml` + `docker-compose.override.yml` now live at the **repo root**, not `backend/`. |

**Final checkpoint (end-to-end):** register → build profile → analyze JD → match → verify skills →
generate → save → edit → download. See `documentation/README.md` for the full feature specs.
