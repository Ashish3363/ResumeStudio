# Saved-Resume Management

**Scope:** MVP

Replaces the earlier "versioning" concept. Resumes are **not** versioned: each tailored
resume is an independent artifact, and editing a saved resume **overwrites it in place**.

## Save vs. Download (distinct actions)
- **Save** — persists the resume as a row in `resumes` (counts toward the cap). Used to keep
  it in the user's profile.
- **Download** — delivers the compiled PDF file to the user. Creates **no** row.

A user can download without saving, or save without downloading.

## The 10-resume cap (FIFO)
- Each user may keep **10 saved resumes**.
- Saving the 11th **evicts the oldest** saved resume (by `created_at`) **and deletes its PDF**
  from object storage.
- Enforced **atomically** on save (transaction/trigger) so a burst of saves can't exceed 10.
- The count is a `COUNT(*)` over `resumes` for the user — there is no counter column.
- Fixed at 10 for all users in MVP; plan-based limits are Phase 2.

## Editing
Editing a saved resume updates the **same row** (`resume_json` overwritten, PDF regenerated).
No history is kept. To keep an alternative, the user generates/saves a new resume instead.

## Actions & endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/resumes` | save current resume → new row (may evict oldest) |
| GET | `/resumes` | list the user's saved resumes |
| GET | `/resumes/{id}` | fetch one saved resume |
| PATCH | `/resumes/{id}` | edit in place (rename and/or content) → PDF regenerated |
| DELETE | `/resumes/{id}` | delete a saved resume (and its PDF) |
| GET | `/resumes/{id}/pdf` | download the PDF (no row change) |

## Storage hygiene
Every path that removes a resume (FIFO eviction or explicit delete) must also remove its
`pdf_url` object from storage to avoid orphaned files.
