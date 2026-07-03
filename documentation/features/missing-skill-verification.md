# Missing-Skill Verification

**Scope:** MVP — **this is the core differentiator.**

## Rule
The AI must **NEVER** add a skill just because it appears in the Job Description.
Every skill in the JD but missing from the resume must be **explicitly confirmed by the user**.

## Flow
1. Match analysis returns `missing_skills` (JD skills absent from the resume).
2. For each missing skill, the user is asked: *"Have you worked with X?"* with options:
   - **Expert**
   - **Intermediate**
   - **Beginner**
   - **Currently Learning**
   - **No Experience**
3. The user answers each one.
4. Answers are sent to `/generate`. Only confirmed skills are written into `ResumeData`
   with `verified = true` and `source = verified`.

## How each answer is treated
| Answer | Result |
|---|---|
| Expert | Included naturally, presented as strong. |
| Intermediate | Included. |
| Beginner | Included as basic knowledge, where appropriate. |
| Currently Learning | Mentioned as in-progress, if suitable. |
| **No Experience** | **Not added.** Never stored, never rendered. |

## Data contract
- Each answer = `SkillVerification { name, choice }`.
- `choice = no_experience` → skill is dropped entirely (no enum value in `ResumeData`).
- All other choices map to a `SkillLevel` and set `verified = true`.

## Enforcement
The generator emits **only** `verified` skills. Even if a prompt misbehaves, an unverified
skill cannot reach the resume. This is the truth policy enforced in data.
