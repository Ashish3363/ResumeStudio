# Job Description Analysis

**Scope:** MVP

## Summary
When the user pastes a Job Description, the AI extracts structure from it into a
`JDAnalysis` object. The AI **extracts only** — it must not invent requirements that
aren't in the text.

## Extracted fields
- Required skills
- Preferred skills
- Technologies
- Frameworks
- Programming languages
- Soft skills
- Certifications
- Experience requirements (e.g. "3+ years backend")
- Responsibilities
- Keywords (ATS)
- Action verbs

## Endpoint
`POST /jd/analyze` → returns `JDAnalysis`, stored in `job_descriptions.analysis_json`.

## Downstream use
- The **matching** module diffs the JD's skill terms against the resume's skills.
- The **generator** uses keywords + action verbs to optimize bullet language.

## Reference
`JDAnalysis` provides `all_skill_terms()` — a flat, de-duplicated, case-insensitive list of
every skill-like term (required + preferred + technologies + frameworks + languages) used by matching.
