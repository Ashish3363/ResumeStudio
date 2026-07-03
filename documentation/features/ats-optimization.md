# ATS Optimization

**Scope:** MVP

## Summary
The platform optimizes resumes for Applicant Tracking Systems across content and structure,
and surfaces an ATS score with concrete suggestions.

## What is optimized
- **Keywords** — pulled from `JDAnalysis`, placed naturally in relevant sections.
- **Formatting** — single-column, standard fonts, selectable text (handled by the template).
- **Section ordering** — `section_order` controls which sections show and their order.
- **Readability** — clear, concise bullets.
- **Bullet structure** — action verb + task + measurable outcome.
- **Action verbs** — favored from the JD's verb list.

## ATS score
Reported in the Match Analysis as `ats_formatting_score`, computed by **rule-based checks**
(deterministic), alongside improvement suggestions.

## Why the template matters for ATS
LaTeX output must produce **selectable text** in a single-column layout with standard fonts —
this is what real ATS parsers can read. Verified as part of PDF generation.

## Relationship to other features
- Score and suggestions live in [Match Analysis](./match-analysis.md).
- Keyword/verb application happens in [Resume Generation](./resume-generation.md).
- Layout guarantees come from [PDF Generation](./pdf-generation.md).
