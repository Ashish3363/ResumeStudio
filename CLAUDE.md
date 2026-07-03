# ResumeStudio — AI Resume Tailoring Platform

> Living project document. Records **finalized decisions**, architecture, and roadmap.
> Update this file whenever a decision changes. This is the source of truth for the build.

---

## 1. What we're building

A production-ready **AI Resume Tailoring Platform** (SaaS) that generates ATS-friendly,
industry-standard resumes tailored to a specific Job Description (JD).

The defining principle is **truthful optimization**: the AI must **never fabricate** skills,
experience, projects, certifications, or achievements. Anything missing must be **explicitly
verified by the user** before it can appear in the resume.

The product behaves like an **AI career coach**, not a text generator.

---

## 2. Finalized decisions

| Area | Decision | Notes |
|---|---|---|
| **Scope** | Lean MVP first | Premium features deferred to Phase 2 (see §6). |
| **PDF engine** | **LaTeX**, compiled via **Tectonic** | Overleaf-grade output. Tectonic chosen over full TeXLive to keep the Docker image small. |
| **Auth** | Roll-your-own **JWT + refresh tokens** | bcrypt/argon2 hashing; refresh-token rotation + revocation. |
| **Database** | **Neon** (managed Postgres) in prod | No self-hosted Postgres in prod. Optional local Postgres via Docker Compose for dev, or a Neon branch. |
| **Editor** | **Structured per-section forms** | Each field maps to JSON; bullets are rich text. No freeform text re-parsing. |
| **Source of truth** | **Structured Resume JSON** | AI controls content only; template controls layout only. |
| **AI** | **Gemini** behind a provider abstraction | Use Gemini structured/JSON-schema output. Never parse free-text JSON. |
| **Frontend** | React 19 + Vite (scaffolded) | Add React Router, TanStack Query, React Hook Form + Zod. |
| **Backend** | FastAPI (Python 3.10+) | Pydantic v2, SQLAlchemy 2.0, Alembic. |
| **Storage** | S3-compatible (Cloudflare R2 or Supabase Storage) | Stores uploaded resumes + generated PDFs. |
| **Deploy** | Backend → Render (Docker) · DB → Neon · Frontend → Vercel | |

### Core architecture principle
```
Resume JSON  →  LaTeX Template Engine  →  Tectonic compile  →  PDF
```
- AI writes **content only**; it never writes LaTeX.
- The template owns **layout only**.
- Every edit/generation updates the JSON and produces a **new immutable version** (never overwrite).
- A skill appears **only** if it was uploaded, manually entered, or explicitly verified by the user.

---

## 3. Tech stack

- **Frontend:** React 19 + Vite · React Router · TanStack Query · React Hook Form + Zod
- **Backend:** FastAPI · Pydantic v2 · SQLAlchemy 2.0 · Alembic
- **DB:** PostgreSQL (Neon prod / local or Neon-branch dev)
- **AI:** Gemini API via `AIProvider` abstraction
- **PDF:** LaTeX via Tectonic (inside Docker)
- **Auth:** JWT access + refresh tokens
- **Storage:** S3-compatible object storage

---

## 4. Backend module structure (`backend/app/`)

Each module is independently maintainable:

- `auth/` — register, login, refresh, password hashing, JWT issue/verify, `get_current_user` dependency
- `users/` — profile, subscription status, generation-quota counter
- `resumes/` — Resume + ResumeVersion CRUD, JSON source-of-truth, rename, history
- `parser/` — PDF (pdfplumber/PyMuPDF) + DOCX (python-docx/mammoth) extraction → LLM structuring
- `jd/` — Job Description analysis (required/preferred skills, keywords, action verbs, …)
- `matching/` — **deterministic** skill/keyword overlap scoring + synonym normalization; LLM only for prose suggestions
- `ai/` — `AIProvider` interface + `GeminiProvider` impl; prompt templates; structured-output contracts
- `generator/` — verified data → optimized resume JSON content + `changes_summary`
- `template/` — Resume JSON → LaTeX (Jinja2 + LaTeX-safe escaping); one universal ATS template, modular for future
- `pdf/` — Tectonic compile service (sandbox, timeout, error capture)
- `storage/` — upload/download abstraction over S3-compatible bucket
- `subscription/` — plan model + free-tier quota check (payments deferred)

### AI provider abstraction (build first, before any Gemini call)
```python
class AIProvider(Protocol):
    def parse_resume(text: str) -> ResumeData
    def analyze_jd(jd_text: str) -> JDAnalysis
    def suggest_improvements(resume: ResumeData, jd: JDAnalysis) -> Suggestions
    def optimize_content(resume: ResumeData, jd: JDAnalysis, verified_skills) -> ResumeData
```
Business logic depends only on this interface. Swapping to OpenAI/Claude later touches only `ai/`.

---

## 5. Data model (4 Postgres tables — finalized, no versioning)

Principle: each fact in one place; JSONB collapses variable structure; derivable data is not stored.
PKs are UUIDv7; FKs cascade from `users`. Full detail in `documentation/02-data-model.md`.

Product facts: **no version history** (each tailored resume is independent; **edit overwrites in
place**); **one career profile per user** (1:1 master truth pool); **saved resumes capped at 10/user
FIFO** (11th evicts oldest row + its stored PDF, atomically; cap = `COUNT(*)`, no counter column);
**Save ≠ Download** (Save persists a row; Download only delivers the PDF).

- `users` (id, full_name, email, password_hash, is_email_verified, profile_picture,
  **token_version**, plan, created_at, updated_at) — `plan` for Phase-2 billing, not enforced in MVP
- `career_profiles` (id, user_id **UNIQUE**, title, **profile_json** JSONB, created_at, updated_at)
  — master truth pool; verified missing-skills written back here
- `job_descriptions` (id, user_id, company_name, job_title, jd_text, parsed_jd_json JSONB, created_at)
- `resumes` (id, user_id, job_description_id FK, resume_name, **resume_json** JSONB, changes_summary
  JSONB, pdf_url, ats_score, overall_match_score, match_report JSONB, created_at, updated_at)
  — saved tailored resumes; flat; capped 10/user FIFO; edited in place

`profile_json` is the source of truth for career data; `resume_json` is a JD-tailored projection.

**Not tables** (folded/derivable): skill verifications → `skills[]` flags; section selection →
`resume_json.section_order`; match report → deterministic scores as columns + optional JSONB;
LaTeX → regenerated; refresh tokens → `users.token_version`; uploads → fold into `career_profiles`;
version history → none (edit in place). **Phase 2 (design later):** `subscriptions`, `payments`.

---

## 6. MVP scope vs. deferred

**MVP (build now):**
Auth → JD input → resume upload/manual input → AI parse & structure → JD analysis →
match report (deterministic core) → **missing-skill verification** → section selection →
AI generation → structured editor (edit in place) → LaTeX/PDF regeneration →
save (cap 10/user FIFO) → download/rename.

**Phase 2 (deferred):**
Stripe payment enforcement · cover-letter generator · interview-question generator ·
LinkedIn optimization · multiple templates. (Data model leaves room for plans/quotas; MVP only
enforces a simple free-tier generation counter.)

---

## 7. Key workflow rules

- **Missing-skill verification (core feature):** after match analysis, diff JD skills vs. resume
  skills. For each missing skill, ask the user their level (Expert / Intermediate / Beginner /
  Currently Learning / No Experience). Include the skill **only** per their answer; "No Experience"
  → excluded. Never auto-include from the JD.
- **Match score:** computed **deterministically** (normalized weighted set overlap) so the same
  input always yields the same score. LLM produces only the qualitative suggestions.
- **Editor:** structured forms; editing a saved resume **overwrites `resume_json` in place** → regenerate LaTeX + PDF. No version history.
- **Saved-resume cap:** 10 per user, FIFO — saving the 11th deletes the oldest row and its stored PDF (atomic). Save persists a row; Download only delivers the PDF.
- **AI transparency:** generator returns a `changes_summary` shown to the user.
- **Truth policy is a hard product rule** — never invent skills, experience, certs, projects, or achievements.

---

## 8. Roadmap (build order)

1. **Scaffold + infra** — FastAPI project, SQLAlchemy + Alembic, Dockerfile w/ Tectonic, docker-compose for dev, env config, connect to Neon.
2. **Auth** — register/login/refresh, JWT, password hashing, refresh-token rotation, `get_current_user`.
3. **AI abstraction + Gemini provider** — structured output contracts (Pydantic schemas).
4. **Resume input** — manual entry endpoints + upload parsing (PDF/DOCX → text → LLM structure).
5. **JD analysis** — endpoint + storage.
6. **Matching** — deterministic score + missing-skill verification flow.
7. **Generator** — verified content optimization + `changes_summary`.
8. **Template engine + PDF** — JSON → LaTeX (escaped) + Tectonic compile + storage upload.
9. **Saved-resume management** — save (persist row), rename, edit-in-place, delete, download; FIFO cap (10/user) with atomic oldest-eviction incl. PDF cleanup.
10. **Frontend** — routing, auth pages, JD/upload/manual flows, match report UI, skill-verification UI, section selector, structured editor, version history, PDF preview/download.
11. **Subscription scaffolding** — plan model + free-tier generation counter (no payments yet).

---

## 9. Security must-dos (LaTeX/Tectonic)

User-controlled text flows into a LaTeX compiler — treat as an injection/RCE risk:
- Compile with **shell-escape disabled**.
- Compile in an **isolated temp dir** with a **hard timeout**.
- **Escape all LaTeX special chars** (`& % $ # _ { } ~ ^ \`) when injecting user JSON into the template.

---

## 10. Verification checklist

- **LaTeX/PDF pipeline (highest risk — test first):** sample JSON → template → Tectonic → valid PDF;
  text is **selectable** (copy out of PDF); single-column ATS layout; special chars don't break or inject.
- **Truth policy:** JD has skills not in resume → none appear until verified; "No Experience" excluded.
- **Match score determinism:** same resume + JD → identical score.
- **Auth:** register → login → protected route → refresh → rotated token works, old refresh revoked.
- **End-to-end:** upload → JD → match report → answer skills → generate → save (row created) →
  edit a section (overwrites in place, PDF regenerated) → download. Save creates a row; download does not.
- **FIFO cap:** save 11 resumes → oldest row and its stored PDF removed; count stays at 10.
- **Deploy smoke test:** Docker image builds with Tectonic, deploys on Render, connects to Neon,
  compiles a PDF within the request timeout.

---

## 11. Current state & setup prerequisites

- **Done:** Fresh Vite + React 19 scaffold in `frontend/`. No backend yet.
- **Local env:** Python 3.10.4 and pip present.
- **Still to install for the full pipeline:**
  - **Tectonic** (LaTeX compiler) — needed for PDF generation.
  - **Docker** — needed for local parity and the Render deploy image.
- **Secrets needed (in `.env`, not committed):** Gemini API key, Neon DB URL, JWT secret, storage credentials.
