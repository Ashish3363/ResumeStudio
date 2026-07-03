# Architecture

## Core data flow
```
Resume JSON  →  LaTeX Template Engine  →  Tectonic compile  →  PDF
```
- AI controls **content only**; it never writes LaTeX.
- The template controls **layout only**.
- Each generated resume is an independent artifact; **editing overwrites in place** (no version history).

## Tailoring pipeline
```
upload/manual → ResumeData JSON ─┐
                                  ├─► matching (deterministic) → MatchReport + missing_skills
JD text → analyze_jd → JDAnalysis ┘
                                  │
        user answers skill questions (Expert / … / No Experience)
                                  ▼
        generate(verified ResumeData, JDAnalysis, section_order)
                                  ▼
        optimized ResumeData JSON → template → LaTeX → Tectonic → PDF → (on Save) resume row
```

## Tech stack
| Layer | Choice |
|---|---|
| Frontend | React 19 + Vite · React Router · TanStack Query · React Hook Form + Zod |
| Backend | FastAPI (Python 3.10+) · Pydantic v2 · SQLAlchemy 2.0 · Alembic |
| Database | PostgreSQL — Neon (prod), local/Neon-branch (dev) |
| AI | Gemini via `AIProvider` abstraction |
| PDF | LaTeX via Tectonic (in Docker) |
| Auth | JWT access + refresh tokens |
| Storage | S3-compatible (Cloudflare R2 or Supabase Storage) |

## Backend module layout (`backend/app/`)
Each module is self-contained (`router.py`, `service.py`, shared `schemas/` + `models/`):

| Module | Responsibility |
|---|---|
| `auth/` | register, login, refresh, hashing, JWT, `get_current_user` |
| `users/` | account profile; `career_profiles` master data (1:1) |
| `resumes/` | saved-resume CRUD, rename, edit-in-place, FIFO cap (10/user) |
| `parser/` | PDF/DOCX extraction → LLM structuring |
| `jd/` | Job Description analysis |
| `matching/` | deterministic match scoring + synonym normalization |
| `ai/` | `AIProvider` interface + `GeminiProvider` + prompts |
| `generator/` | verified data → optimized resume JSON + `changes_summary` |
| `template/` | Resume JSON → LaTeX (escaped) |
| `pdf/` | Tectonic compile (sandbox, timeout) |
| `storage/` | upload/download over S3-compatible bucket |
| `subscription/` | plan model + free-tier quota check |

## Sync vs. async (decision: deferred)
MVP runs the pipeline **synchronously** (request/response). The `generator/` and `pdf/`
services are structured behind a service interface so they can move to **background jobs**
(e.g. Celery/RQ + Redis) later **without changing the API surface**.

## API surface (MVP)
| Module | Endpoints |
|---|---|
| auth | `POST /register` · `POST /login` · `POST /refresh` · `POST /logout` |
| profile | `GET /profile` · `PUT /profile` · `POST /profile/upload` |
| resumes | `GET /resumes` · `POST /resumes` (save) · `GET /resumes/{id}` · `PATCH /resumes/{id}` (edit/rename) · `DELETE /resumes/{id}` · `GET /resumes/{id}/pdf` |
| jd | `POST /jd/analyze` |
| matching | `POST /match` → report + missing skills |
| generator | `POST /generate` → optimized `resume_json` + `changes_summary` |
## File structure (backend)

```
backend/
├── app/
│   ├── main.py · config.py · database.py       # entrypoint, settings, DB session
│   ├── models/       base, user, career_profile, job_description, resume   # 4 tables
│   ├── schemas/      resume, jd, matching, auth, profile                   # Pydantic contracts
│   ├── core/         security, deps, exceptions                            # JWT, get_current_user
│   ├── auth/         router + service                                      # register/login/refresh
│   ├── users/        router + service                                      # account + career profile
│   ├── resumes/      router + service                                      # save, edit-in-place, FIFO cap
│   ├── parser/       router, service, extractors                           # PDF/DOCX → text → LLM
│   ├── jd/           router + service                                      # JD analysis
│   ├── matching/     router, service, synonyms                             # deterministic scoring
│   ├── ai/           provider, gemini, prompts/                            # AIProvider abstraction
│   ├── generator/    router + service                                      # verified data → resume_json
│   ├── template/     service, escaping, templates/ats_resume.tex.j2        # JSON → LaTeX
│   ├── pdf/          service                                               # Tectonic compile
│   ├── storage/      service                                               # S3-compatible
│   └── subscription/ service                                               # plan/quota (Phase 2)
├── alembic/          env.py, versions/                                     # migrations
├── tests/            conftest.py
├── Dockerfile · docker-compose.yml · requirements.txt · alembic.ini
└── .env.example · .gitignore · README.md
```

### Composition conventions
- **`main.py`** is the composition root only: creates the `FastAPI` app, sets CORS + lifespan,
  and `include_router(...)`s each module under an `/api` prefix. No business logic.
- **`config.py`** exposes one typed `settings` singleton (`pydantic-settings`) read from env/`.env`.
  Required secrets have no default (fail-fast at boot). The `10` saved-resume cap lives here as
  `SAVED_RESUME_CAP` — never hardcoded elsewhere.
- Every module's `router.py` exposes a module-level `router = APIRouter()`; `service.py` holds the
  logic and depends only on `schemas/`, `models/`, and the `AIProvider` interface.
