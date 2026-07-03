# Deployment

| Component | Target |
|---|---|
| Backend | Render (Docker) |
| Database | Neon (managed Postgres) |
| Frontend | Vercel |
| Storage | Cloudflare R2 or Supabase Storage (S3-compatible) |

## Backend on Render (Docker)
A Dockerfile is required because the backend needs the LaTeX toolchain installed.
- Use **Tectonic** (single binary, fetches packages on demand, cached) instead of full
  TeXLive (~4–5 GB) to keep the image small and deploys fast.
- Fall back to a curated `texlive-latex-recommended` + fonts install only if a needed
  package can't be fetched by Tectonic.

## Database on Neon
- Managed Postgres; **no self-hosted Postgres in production.**
- Use a Neon branch for staging.
- Connection string supplied via env (`DATABASE_URL`).

## Local development
- `docker-compose` with backend + (optional) local Postgres, **or** point dev at a Neon branch.

## Secrets (env vars — never committed)
- `GEMINI_API_KEY`
- `DATABASE_URL` (Neon)
- `JWT_SECRET` (+ access/refresh TTL settings)
- Storage credentials (bucket, key, secret, endpoint)

## Local prerequisites still to install
- **Tectonic** (LaTeX compiler)
- **Docker** (local parity + Render image)
- Python 3.10+ present on dev machine (3.10.4 confirmed)
