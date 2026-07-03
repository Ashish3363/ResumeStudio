# Resume Generation

**Scope:** MVP

## Summary
Generates an ATS-friendly resume from **verified information only**. The AI optimizes
language while preserving factual accuracy — it never invents technologies or accomplishments.

## Endpoint
`POST /generate` — inputs: the user's `career_profiles.profile_json`, `JDAnalysis`, the user's
skill verifications, and the selected `section_order`. Output: optimized `resume_json` + a
`changes_summary`. This is a transient result until the user **saves** it (see
[Saved-Resume Management](./saved-resume-management.md)).

## What gets optimized
- Professional summary
- Skills (ordering/grouping)
- Experience & project bullet points (action verbs, measurable outcomes)
- Keyword placement (from `JDAnalysis`)
- Section ordering

## Example rewrite (language only — facts preserved)
> Before: "Built an ecommerce website."
> After: "Developed a responsive e-commerce platform using React, Express.js and MongoDB
> with JWT authentication and REST APIs."

(Only valid if React/Express/MongoDB/JWT are actually part of the user's verified data.)

## Section selection
Before generation the user chooses which sections appear (summary, skills, education,
experience, internships, projects, certifications, achievements, languages, volunteer,
publications, awards, interests). This is stored as `section_order`; only listed sections render.

## Resume length
Content-driven: defaults to one page; expands to two when sections/experience warrant it.
No hard line limit.

## AI transparency
The generator returns a `changes_summary`, shown to the user, e.g.:
```
✓ Improved summary
✓ Rewrote project descriptions
✓ Added action verbs
✓ Reordered skills
✓ Improved ATS keywords
```

## Truth guard
Only `verified` skills and existing factual content are used. See Missing-Skill Verification.
