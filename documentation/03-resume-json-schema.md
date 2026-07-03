# Resume JSON Schema — Single Source of Truth

This contract is shared by the AI provider, the database (`resumes.resume_json` and, for the
master profile, `career_profiles.profile_json`),
the structured editor forms, and the LaTeX template engine. Get this right and the rest is
plumbing.

> A reference Pydantic v2 implementation exists at `backend/app/schemas/resume.py`.
> This document is the canonical description.

## Design rules
1. **Truth enforced in data** — every skill carries `verified` + `source`. The generator
   MUST refuse to emit any skill where `verified = false`. A "No Experience" answer means
   the skill is simply absent (never stored).
2. **`section_order` lives in the JSON** — section selection and ATS reordering are just
   edits to this list; no separate state.
3. **Dates are free-form strings** (`"2023-01"`, `"Jan 2023"`, `"present"`) — the template
   handles display.

## Shape
```jsonc
{
  "basics": {
    "full_name": "", "email": "", "phone": "", "location": "",
    "links": [{ "label": "GitHub", "url": "" }]
  },
  "summary": "Professional summary text",

  "skills": [
    { "name": "React", "level": "expert", "source": "uploaded", "verified": true }
  ],

  "experience": [
    { "company": "", "role": "", "location": "",
      "start": "2023-01", "end": "present", "bullets": ["..."] }
  ],
  "internships": [ /* same shape as experience */ ],

  "projects": [{ "name": "", "tech": ["..."], "bullets": ["..."], "link": "" }],

  "education": [{ "school": "", "degree": "", "field": "", "start": "", "end": "", "details": "" }],

  "certifications": [{ "name": "", "issuer": "", "date": "" }],
  "achievements": ["..."],
  "languages": [{ "name": "", "proficiency": "" }],

  // Schema-ready optional sections
  "awards": ["..."],
  "publications": ["..."],
  "volunteer": [ /* same shape as experience */ ],
  "interests": ["..."],

  "section_order": ["summary", "skills", "experience", "projects", "education"]
}
```

## Enums
| Field | Values |
|---|---|
| `skills[].level` | `expert` · `intermediate` · `beginner` · `learning` |
| `skills[].source` | `uploaded` · `manual` · `verified` |
| `section_order[]` | `summary` `skills` `experience` `internships` `projects` `education` `certifications` `achievements` `languages` `awards` `publications` `volunteer` `interests` |

> "No Experience" has **no** enum value on purpose — such skills are never added.

## Invariant
`verified_skills = [s for s in skills if s.verified]` is the **only** set of skills the
generator and template are allowed to render.
