# Subscription

**Scope:** MVP (scaffolding only) · Payments are **Phase 2**

## MVP
- `users.plan` (`free` | `premium`) exists but is **not enforced** yet.
- The only active limit is the **10 saved-resumes cap** per user (FIFO), enforced by a
  `COUNT(*)` over `resumes` — not a plan feature and not a counter column. See
  [Saved-Resume Management](./saved-resume-management.md).
- No payment provider integrated yet.

## Plans
### Free
- Up to 10 saved resumes (FIFO)
- Basic ATS analysis
- Resume editing (in place)
- PDF download

### Premium (Phase 2)
- More/unlimited saved resumes
- Resume parser
- JD optimization
- Cover Letter Generator
- Interview Question Generator
- Advanced ATS Analysis
- LinkedIn Profile Optimization

## Phase 2 — Payments
- Provider: **Stripe**.
- Subscription state driven by **Stripe webhooks**.
- Dedicated `subscriptions` + `payments` tables will own plan changes and entitlement checks
  (designed but not built in MVP — see [Data Model](../02-data-model.md)).

## Design note
`users.plan` is present so plan-based entitlement checks (e.g. raising the saved-resume cap)
can be layered on without reworking the core tables when payments land.
