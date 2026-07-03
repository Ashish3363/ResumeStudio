# Data Model

PostgreSQL (Neon). SQLAlchemy 2.0 ORM + Alembic migrations. **4 tables.**
`profile_json` (JSONB) is the source of truth for the user's career data; `resume_json`
is a tailored, JD-specific projection of it.

## Product facts that shape the model
- **No version history.** Each tailored resume is an independent artifact — there is no
  edit-chain. Editing a saved resume **overwrites in place**. (No `resume_versions` table.)
- **Master profile is 1:1 with the user** — one `career_profiles` row per user, reused across
  every tailored resume. Missing-skill verification writes confirmed skills back here so they
  persist for future resumes.
- **Saved resumes are capped at 10 per user, FIFO.** Saving the 11th deletes the oldest row
  **and its PDF in object storage**, enforced atomically. The cap is a `COUNT(*)` over
  `resumes` — no counter column.
- **Save ≠ Download.** Save persists a `resumes` row (counts toward 10). Download just delivers
  the PDF file and creates no row.

## Design principles
- Each fact lives in exactly one place — no duplication of mutable data.
- JSONB collapses variable structure that would otherwise explode into many tables.
- Derivable data is **not** stored (recompute instead); only binary artifacts (PDF) are persisted externally.
- PKs are **UUIDv7** (sortable, non-guessable in URLs, object-storage-friendly).
- FKs cascade from `users` downward (`ON DELETE CASCADE`).

## What is intentionally NOT a table
| Concept | Where it lives instead |
|---|---|
| Skill verifications (Expert/…/No Experience) | `profile_json` / `resume_json` `skills[]` (`verified`, `level`); "No Experience" = absent |
| Section selection / order | `resume_json.section_order` |
| Match report | Deterministic scores stored as columns; full report as optional JSONB on `resumes` |
| Generated LaTeX | Derivable from `resume_json` + template → regenerated, never stored |
| Refresh tokens | `users.token_version` (see Authentication) — no token rows |
| Uploaded file record | Original file URL + parsed data fold into `career_profiles` |
| Resume version history | None — resumes are edited in place, not versioned |
| Save quota counter | `COUNT(*)` over `resumes` per user — no column |

## Tables

### `users`
| Column | Type | Notes |
|---|---|---|
| id | UUIDv7 / PK | |
| full_name | text | account name (≠ resume name) |
| email | text, unique, not null | |
| password_hash | text, not null | bcrypt/argon2 |
| is_email_verified | bool, default false | verification flow is Phase 2 |
| profile_picture | text, nullable | avatar URL |
| token_version | int, default 0 | bump to revoke all refresh tokens |
| plan | text, default `free` | kept for Phase-2 billing; not enforced in MVP |
| created_at / updated_at | timestamptz | |

### `career_profiles` — master truth pool (1:1 with user)
| Column | Type | Notes |
|---|---|---|
| id | UUIDv7 / PK | |
| user_id | FK → users, **UNIQUE** (CASCADE) | one per user |
| title | text, nullable | optional label |
| profile_json | JSONB, not null | personal info, skills (with `verified`/`level`), education, experience, projects, certifications, languages, links, achievements |
| created_at / updated_at | timestamptz | |

> Fold note: at strict 1:1 this could collapse into `users`. Kept separate so the hot `users`
> table stays lean for auth and the large `profile_json` (TOAST) loads only when needed.

### `job_descriptions`
| Column | Type | Notes |
|---|---|---|
| id | UUIDv7 / PK | |
| user_id | FK → users (CASCADE) | index |
| company_name | text, nullable | |
| job_title | text, nullable | |
| jd_text | text, not null | pasted JD |
| parsed_jd_json | JSONB, not null | `JDAnalysis` output |
| created_at | timestamptz | |

### `resumes` — saved tailored resumes (flat; capped 10/user FIFO; edited in place)
| Column | Type | Notes |
|---|---|---|
| id | UUIDv7 / PK | |
| user_id | FK → users (CASCADE) | index; cap is COUNT per user |
| job_description_id | FK → job_descriptions, nullable | what it was tailored to |
| resume_name | text | user-renamable |
| resume_json | JSONB, not null | **source of truth for this resume** (see Resume JSON Schema) |
| changes_summary | JSONB, nullable | AI change list (transparency) |
| pdf_url | text, nullable | compiled PDF in object storage |
| ats_score | int, nullable | deterministic (cache) |
| overall_match_score | int, nullable | deterministic (cache) |
| match_report | JSONB, nullable | strong matches, missing keywords, LLM suggestions |
| created_at / updated_at | timestamptz | |

## Rules
- **Save** creates a `resumes` row; **edit** overwrites the same row (PDF regenerated); **download** creates nothing.
- Saving beyond 10 removes the oldest resume **and its stored PDF**, atomically, so the count stays at 10.
- Deleting a user cascades to their profile, job descriptions, and resumes.

## Phase 2 (design later, not built now)
- `subscriptions` (plan, status, limits, period)
- `payments` (provider, transaction, amount, status) — Stripe, webhook-driven
