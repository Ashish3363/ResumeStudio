# Match Analysis

**Scope:** MVP

## Summary
Compares the user's `ResumeData` against the `JDAnalysis` and produces a `MatchReport`.
The **score is deterministic** (computed in code), so the same resume + JD always yields
the same number. The LLM contributes **only** the qualitative suggestions.

## Endpoint
`POST /match` → returns `MatchReport` including the `missing_skills` that drive verification.

## Report contents
- **Overall match** (0–100)
- **Skills match**, **keyword match**, **experience match**, **ATS formatting score**
- **Strong matches** — skills present in both resume and JD
- **Missing skills** — in JD, absent from resume (each flagged required vs preferred)
- **Missing keywords**
- **Suggestions** — LLM-authored qualitative improvements

## Scoring (deterministic)
- Normalize terms (lowercase, trim, synonym map e.g. "JS" → "JavaScript").
- Compute weighted set overlap: required skills weighted higher than preferred.
- Keyword match = overlap of JD keywords found in resume text.
- ATS formatting score = rule-based checks on the resume structure.

Why deterministic: an LLM-estimated percentage changes run-to-run and users notice. Code-based
scoring is reproducible; the LLM is reserved for prose only.

## Example
```
Overall Match: 87%
Strong: React, Node.js, REST API
Missing: Docker, AWS, Redis
Suggestions: strengthen summary; add measurable achievements to Project 2
```

## Next step
`missing_skills` is handed to the Missing-Skill Verification flow.
