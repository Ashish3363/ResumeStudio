# Resume Input

**Scope:** MVP

Two ways to provide resume information. Both populate the user's **career profile**
(`career_profiles.profile_json`) — the master truth pool that every tailored resume is
generated from. (See [Data Model](../02-data-model.md).)

## Option 1 — Manual input
The user fills structured fields. Only fields needed for the selected sections are collected:
Full Name, Contact, Education, Skills, Projects, Experience, Internships, Certifications,
Achievements, Languages, Links (GitHub/LinkedIn/Portfolio).

- Endpoint: `PUT /profile` (upserts `profile_json`).
- Manually entered skills get `source = manual`, `verified = true`.

## Option 2 — Upload existing resume
The user uploads a PDF or DOCX. The AI extracts and structures the **content only** —
the old formatting is discarded entirely.

- Endpoint: `POST /profile/upload`
- Pipeline: file → text extraction → `AIProvider.parse_resume(text)` → structured data.
- Text extraction: PDF via pdfplumber/PyMuPDF; DOCX via python-docx/mammoth.
- Extracted skills get `source = uploaded`, `verified = true`.
- The extracted data **populates `career_profiles.profile_json`** (merged with anything already
  there). No separate uploads table; the raw file may optionally be kept in storage for provenance.

## Notes
- Extraction quality varies by file; the LLM structures and cleans the raw text.
- Extracted data populates editable fields (see Resume Editor) so the user can correct it.

## Truth policy
Only content actually present in the upload or typed by the user is captured here. Nothing is invented.
