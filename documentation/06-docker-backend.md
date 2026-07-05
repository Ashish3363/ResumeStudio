# Backend Dockerfile — Implementation Guide

> How to write `backend/Dockerfile` for ResumeStudio, in detail.
> This is the **first** Docker artifact to build because it carries the riskiest
> piece — the **Tectonic** LaTeX toolchain. Prove this image before touching
> `frontend/Dockerfile` or Compose.
>
> Companion files (documented separately): `frontend/Dockerfile`,
> `docker-compose.yml` (base) + `docker-compose.override.yml` (dev).

---

## 0. Goals for this image

| Goal | How we achieve it |
|---|---|
| Small final image | `python:3.13-slim` base + **multi-stage** build (compilers/curl stay in the builder) |
| Fast rebuilds | Copy `requirements.txt` and install **before** copying source (layer caching) |
| One file, two modes | Named **build targets**: `dev` (hot reload, source bind-mounted) and `prod` (source baked in) |
| Reproducible LaTeX | Fetch the **Tectonic static binary** + **pre-warm** its bundle into a layer |
| Safe under user input | Run as a **non-root** user (backend shells out to Tectonic on user text — RCE surface) |

The design is **three stages**: `base` → `builder` → (`dev` | `prod`). `dev` and
`prod` both inherit from `base` and copy artifacts out of `builder`.

```
        ┌─────────┐
        │  base   │  slim + OS runtime deps + non-root user + env
        └────┬────┘
             │
       ┌─────┴─────┐
       │  builder  │  venv + pip install + download Tectonic binary
       └─────┬─────┘
             │  (copy venv + tectonic binary out)
        ┌────┴────┬──────────┐
        │   dev   │   prod   │
        └─────────┴──────────┘
```

---

## 1. Prerequisite: `.dockerignore` (write this first)

Create `backend/.dockerignore` **before** the Dockerfile, so your very first
build has a clean, small context and no secrets leak into image layers.

Exclude at least:

```
.venv
venv
__pycache__
*.pyc
.env
.git
tests
*.md
alembic/versions/*.pyc
```

> Why it matters: without this, `COPY . .` drags your local `.venv/`, `.git/`,
> and **`.env`** into the build context. That bloats the image and can bake
> secrets into a layer that survives even if you delete the file later.

---

## 2. Stage `base` — common foundation

`FROM python:3.13-slim AS base`

Do here, once, everything both `dev` and `prod` need at **runtime**:

1. **Environment variables** (set with `ENV`):
   - `PYTHONUNBUFFERED=1` — logs stream immediately (no buffering); essential for Docker log capture.
   - `PYTHONDONTWRITEBYTECODE=1` — don't scatter `.pyc` files in the container.
   - `PATH="/opt/venv/bin:$PATH"` — put the venv (copied in later) first on PATH so `python`/`uvicorn`/`alembic` resolve to it without activation.
   - `TECTONIC_CACHE_DIR=/home/appuser/.cache/Tectonic` — pin Tectonic's bundle cache to a path the non-root user owns (details in §5).

2. **Runtime OS packages** Tectonic needs (install with `apt-get`, then clean up):
   - `ca-certificates` — Tectonic fetches its LaTeX bundle over HTTPS on first run.
   - `fontconfig` — Tectonic discovers/uses fonts through it.
   - End the `RUN` with `rm -rf /var/lib/apt/lists/*` **in the same layer** to keep the apt index out of the image.
   - Use `apt-get install -y --no-install-recommends` to avoid pulling suggested extras.

3. **Non-root user**:
   - Create a system user+group, e.g. `appuser` (`useradd --create-home appuser`).
   - `--create-home` matters because `TECTONIC_CACHE_DIR` lives under `/home/appuser`.
   - Don't switch to it yet with `USER` — the `builder` stage needs to install packages. Switch in `dev`/`prod`.

4. `WORKDIR /app`.

> **One `RUN` for apt.** Chain `apt-get update && apt-get install ... && rm -rf ...`
> in a single `RUN` so the cleanup lands in the same layer as the install —
> otherwise the deleted files still occupy the earlier layer.

---

## 3. Stage `builder` — install into an isolated venv

`FROM base AS builder`

This stage holds everything you **don't** want in the final image (build tools,
pip's download cache, curl). Nothing here is copied forward except the venv and
the Tectonic binary.

1. **Install build-time OS deps** you'll discard: `curl`, `tar`/`xz-utils`
   (to fetch + extract Tectonic). Same one-`RUN` + cleanup pattern.

2. **Create the venv and install Python deps** with cache disabled:
   - `python -m venv /opt/venv`
   - `COPY requirements.txt .`  ← copy **only** the manifest first
   - `pip install --no-cache-dir --upgrade pip`
   - `pip install --no-cache-dir -r requirements.txt`
   - `--no-cache-dir` keeps pip's wheel cache out of the layer (smaller image).
   - Because the venv is at `/opt/venv` and `base` already put it on `PATH`, `pip` here targets the venv automatically.

   > **Layer-cache win:** copying `requirements.txt` alone (not the whole app)
   > means editing your Python source later does **not** invalidate this slow
   > `pip install` layer. Only a change to `requirements.txt` re-runs it.

3. **Fetch the Tectonic binary** — see §4 (do it in this stage).

---

## 4. Installing Tectonic (the tricky part)

Tectonic ships a **self-contained static binary** on GitHub Releases — no Rust
toolchain, no TeXLive. Two ways to get it; pick one.

### Option A — official install script (simplest)
Tectonic publishes a one-liner that detects the platform and drops the binary in
the current directory:

```
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh
```

Run it in `builder`, then move the resulting `./tectonic` to a known path like
`/opt/tectonic/tectonic`.
- **Pro:** always grabs a working current release.
- **Con:** unpinned — the version can drift between builds. For reproducibility, prefer Option B.

### Option B — pin an exact release asset (recommended for reproducibility)
Download a specific versioned asset from
`https://github.com/tectonic-typesetting/tectonic/releases`. The Linux asset is
the **musl static** build, named like:

```
tectonic-<VERSION>-x86_64-unknown-linux-musl.tar.gz
```

Steps in `builder`:
1. `curl -fsSL -o tectonic.tar.gz <that release URL>`
2. `tar -xzf tectonic.tar.gz`
3. `mkdir -p /opt/tectonic && mv tectonic /opt/tectonic/`

Pin `<VERSION>` explicitly (e.g. `0.15.0`) so every build gets the same binary.
Record the version in a comment.

> **Arch note:** the `x86_64` asset is correct for Render and typical CI/Linux
> hosts. If you build on an Apple-Silicon Mac with a native arm64 image you'd
> need the `aarch64` asset — but your deploy target (Render) is x86_64, and
> Compose on Windows runs x86_64 too, so `x86_64-unknown-linux-musl` is right.

---

## 5. Pre-warming the Tectonic bundle (do NOT skip)

On its **first** compile, Tectonic downloads a large LaTeX support bundle over
the network and caches it. If you don't pre-warm, the **first user's PDF request
hangs** on that download (and it fails entirely if the prod host blocks egress).

Bake the bundle into an image layer instead. This is best done in the **final
stages** (`dev`/`prod`) *after* the Tectonic binary and the non-root user's cache
dir are in place — because the cache must be owned by `appuser`.

The move:
1. Ensure `TECTONIC_CACHE_DIR` (set in `base`) points under `/home/appuser` and that dir is owned by `appuser`.
2. As `appuser`, compile a throwaway minimal document so the bundle populates the cache:
   - Write a tiny file, e.g. `\documentclass{article}\begin{document}warmup\end{document}`.
   - Run `tectonic <that file>` (Tectonic's default subcommand compiles a single file).
   - Delete the throwaway `.tex`/`.pdf`; the **cache** is what you're keeping.

> **Ordering gotcha:** if you pre-warm as `root` but run as `appuser`, the cache
> sits in root's home and `appuser` can't read it → it re-downloads at runtime.
> Pre-warm **after** `USER appuser`, with `TECTONIC_CACHE_DIR` under that user's home.

> **Trade-off:** pre-warming makes the image larger (the bundle is sizable) but
> makes runtime fast and network-independent. For a PDF-generating service this
> is the correct trade. If image size ever becomes critical, the alternative is a
> persistent cache volume mounted at `TECTONIC_CACHE_DIR` — but that's a Compose/
> deploy concern, not the Dockerfile's job. Default: pre-warm.

---

## 6. Stage `dev` — hot reload, source bind-mounted

`FROM base AS dev`

1. **Copy artifacts from `builder`:**
   - `COPY --from=builder /opt/venv /opt/venv`
   - `COPY --from=builder /opt/tectonic/tectonic /usr/local/bin/tectonic`
   - (`/usr/local/bin` is already on PATH, so `tectonic` resolves globally.)
2. **Do NOT `COPY app/`.** In dev the source lives on the host and is
   **bind-mounted** into `/app` by `docker-compose.override.yml`. Baking it in
   would just be shadowed by the mount.
3. **Ownership + user:** `chown` `/home/appuser` (and its cache dir) to `appuser`, then `USER appuser`.
4. **Pre-warm** the Tectonic bundle here (§5), as `appuser`.
5. **CMD:** run uvicorn with reload and bound to all interfaces:
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
   - `--host 0.0.0.0` is **mandatory** — the default `127.0.0.1` is unreachable from outside the container.
   - `--reload` watches the bind-mounted source for live changes.

---

## 7. Stage `prod` — source baked in, no reload

`FROM base AS prod`

1. **Copy artifacts from `builder`** (same two `COPY --from=builder` lines as dev).
2. **Copy the application source in:** `COPY app/ ./app` (and `alembic/`,
   `alembic.ini` if you run migrations from the image). In prod there is **no**
   bind mount — the code must be inside the image.
3. **Ownership + user:** `chown -R appuser /app /home/appuser`, then `USER appuser`.
4. **Pre-warm** the Tectonic bundle here too (§5), as `appuser`.
5. **`EXPOSE 8000`** (documentation of the port).
6. **CMD:** uvicorn **without** `--reload`, optionally with workers:
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2`
   - No `--reload` in prod (it's slower and watches files you won't change).
   - Tune `--workers` to the host; start with 2.

> **Migrations are not in CMD.** Don't run `alembic upgrade head` as part of the
> server start command — with multiple workers/instances they'd race. Run
> migrations as a separate, deliberate step (documented in the Compose guide).

---

## 8. `COPY` order = cache strategy (the rule to internalize)

Docker caches layers top-to-bottom and invalidates everything **after** the first
changed layer. So order from **least** to **most** frequently changing:

1. Base image + OS deps (rarely change)
2. `COPY requirements.txt` + `pip install` (change only when deps change)
3. Tectonic download (changes only when you bump the pinned version)
4. `COPY app/` (changes constantly — **last**, and only in `prod`)

Get this order wrong (e.g. `COPY . .` before `pip install`) and every one-line
code edit re-runs the whole dependency install.

---

## 9. Build & verify (prove each risk before moving on)

Build a **specific target** with `--target`:

```
# Build the dev image
docker build --target dev -t resumestudio-backend:dev ./backend

# Build the prod image
docker build --target prod -t resumestudio-backend:prod ./backend
```

Then verify, hardest-risk first:

1. **Tectonic installed:**
   `docker run --rm resumestudio-backend:prod tectonic --version`
   → prints a version. Proves the binary fetch + copy worked.

2. **Bundle pre-warmed (offline compile):**
   `docker run --rm --network none resumestudio-backend:prod tectonic --help`
   then, better, exec in and compile a tiny `.tex` with `--network none` — it
   should succeed **without** network, proving the cache is baked in.

3. **App imports under the venv:**
   `docker run --rm resumestudio-backend:prod python -c "import app.main"`
   (Note: this needs `DATABASE_URL` etc. if `config.py` validates on import —
   pass a dummy `-e DATABASE_URL=... -e JWT_SECRET=... -e GEMINI_API_KEY=...`
   or defer settings validation. Expect this and provide env.)

4. **Runs as non-root:**
   `docker run --rm resumestudio-backend:prod whoami` → `appuser`, not `root`.

5. **Image size sanity:**
   `docker images resumestudio-backend` → the `prod` tag should be far smaller
   than a naive single-stage build (the builder's curl/tar/pip-cache are gone).

> During iteration, rebuild **only this service** rather than the whole stack:
> `docker compose build backend` (once Compose exists), or the targeted
> `docker build --target dev ...` above.

---

## 10. Common pitfalls (checklist)

- [ ] `--host 0.0.0.0` in both CMDs (else unreachable from host).
- [ ] Pre-warm happens **after** `USER appuser`, with cache under `/home/appuser`.
- [ ] `.dockerignore` excludes `.env`, `.venv`, `.git` (no secret/bloat leakage).
- [ ] apt install + cleanup (`rm -rf /var/lib/apt/lists/*`) in **one** `RUN`.
- [ ] `--no-cache-dir` on every `pip install`.
- [ ] `requirements.txt` copied **before** source (cache).
- [ ] Source `COPY`'d only in `prod`, never in `dev` (dev bind-mounts it).
- [ ] Tectonic version **pinned** (Option B) for reproducible builds.
- [ ] `ca-certificates` + `fontconfig` present in the **final** stage, not just builder.
- [ ] Final `USER appuser` set (verify with `whoami`).

---

## 11. What comes next (not this file)

1. `frontend/Dockerfile` — multi-stage `node:22-slim` build → `nginx:1.27-alpine` serve, with `dev`/`build`/`prod` targets.
2. `docker-compose.yml` (base, prod-shaped) + `docker-compose.override.yml` (dev: local `db`, bind mounts, `@db:5432`).
3. Migration workflow: `docker compose run --rm backend alembic upgrade head`.

Once `tectonic --version` and an **offline** compile both pass inside the image,
this Dockerfile is done and you can wire it into Compose.
