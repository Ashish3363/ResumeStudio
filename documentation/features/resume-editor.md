# Resume Editor

**Scope:** MVP

## Summary
After generation the user edits the resume through **structured per-section forms** —
never LaTeX, never a freeform text blob. Each field maps directly to `ResumeData`, so
there is no lossy re-parsing.

## Why structured forms (not a plain-text editor)
The Resume JSON is the source of truth. A freeform text editor would require re-parsing
edited prose back into JSON, which is lossy and error-prone. Structured forms keep the
JSON authoritative: every field binds to a JSON path; bullet points are rich text.

## Sections edited
Professional Summary, Skills, Projects, Experience, Education, and any other selected
sections — each as its own form group.

## Edit flow (overwrite in place — no versioning)
1. User edits a section of a saved resume.
2. Save → `PATCH /resumes/{id}` updates `resume_json` on the **same row** (overwrites; no history).
3. Backend regenerates LaTeX + PDF automatically.
4. Updated PDF preview + download are returned.

> To keep an alternative instead of overwriting, the user generates and saves a new resume.
> See [Saved-Resume Management](./saved-resume-management.md).

## User never touches LaTeX
The user edits structured content only; LaTeX and PDF are byproducts the system manages.
