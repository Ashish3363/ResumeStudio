# ResumeStudio — Documentation

Structured documentation for the AI Resume Tailoring Platform. Each feature is
documented in its own file. This is the human-readable spec; `CLAUDE.md` in the
repo root holds the condensed decision record.

## Start here
- [Flow of Code (backend build order)](./flow-of-code.md) — the step-by-step order to build the backend, file by file

## Foundations
- [Product Overview](./00-product-overview.md) — what we're building and the core principle
- [Architecture](./01-architecture.md) — system shape, backend modules, request flow
- [Data Model](./02-data-model.md) — Postgres tables
- [Resume JSON Schema](./03-resume-json-schema.md) — the single source of truth
- [AI Provider Abstraction](./04-ai-provider.md) — provider-agnostic AI layer
- [Deployment](./05-deployment.md) — Render, Neon, Vercel, storage

## Features
- [Authentication](./features/authentication.md)
- [Resume Input](./features/resume-input.md) — manual entry + upload/parsing
- [Job Description Analysis](./features/jd-analysis.md)
- [Match Analysis](./features/match-analysis.md)
- [Missing-Skill Verification](./features/missing-skill-verification.md) — the core differentiator
- [Resume Generation](./features/resume-generation.md)
- [PDF Generation](./features/pdf-generation.md) — LaTeX + Tectonic
- [Resume Editor](./features/resume-editor.md)
- [Saved-Resume Management](./features/saved-resume-management.md) — save/download, 10-resume FIFO cap
- [ATS Optimization](./features/ats-optimization.md)
- [Subscription](./features/subscription.md)

## Status legend
Each feature doc marks scope as **MVP** or **Phase 2**.
