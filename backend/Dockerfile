# Backend image: Python 3.10+ base + Tectonic. (TODO)

# Multi-stage image for the ResumeStudio FastAPI backend.
# Stages: base -> builder -> (dev | prod)
# Build a target explicitly:  docker build --target dev  -t resumestudio-backend:dev  .
#                             docker build --target prod -t resumestudio-backend:prod .

# ---------- base: shared runtime foundation ----------
FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    TECTONIC_CACHE_DIR=/home/appuser/.cache/Tectonic

# Runtime OS deps Tectonic needs: HTTPS bundle fetch + font discovery.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Non-root service user; --create-home because the Tectonic cache lives in $HOME.
RUN useradd --create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

# ---------- builder: venv + deps + tectonic (nothing here ships to final) ----------
FROM base AS builder

# Build-time only tools, discarded with this stage.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl tar \
    && rm -rf /var/lib/apt/lists/*

# Python deps into an isolated venv. requirements.txt copied ALONE first = cache win.
RUN python -m venv /opt/venv
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Tectonic static binary — PINNED for reproducible builds.
# Bump TECTONIC_VERSION to upgrade; asset list: github.com/tectonic-typesetting/tectonic/releases
ARG TECTONIC_VERSION=0.16.9
RUN curl --proto '=https' --tlsv1.2 -fsSL \
        "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40${TECTONIC_VERSION}/tectonic-${TECTONIC_VERSION}-x86_64-unknown-linux-musl.tar.gz" \
        -o /tmp/tectonic.tar.gz \
    && mkdir -p /opt/tectonic \
    && tar -xzf /tmp/tectonic.tar.gz -C /opt/tectonic \
    && rm /tmp/tectonic.tar.gz


# ---------- dev: hot reload, source bind-mounted (NOT copied) ----------
FROM base AS dev

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/tectonic/tectonic /usr/local/bin/tectonic

RUN mkdir -p "$TECTONIC_CACHE_DIR" && chown -R appuser:appuser /home/appuser
USER appuser

# Pre-warm the LaTeX bundle into a layer so the first runtime compile is offline+fast.
RUN printf '\\documentclass{article}\\begin{document}warmup\\end{document}' > /tmp/warmup.tex \
    && tectonic /tmp/warmup.tex \
    && rm -f /tmp/warmup.tex /tmp/warmup.pdf

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

# ---------- prod: source baked in, no reload ----------
FROM base AS prod

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/tectonic/tectonic /usr/local/bin/tectonic

# App source lives inside the image in prod (no bind mount).
COPY alembic.ini ./alembic.ini
COPY alembic/ ./alembic
COPY app/ ./app

RUN mkdir -p "$TECTONIC_CACHE_DIR" && chown -R appuser:appuser /app /home/appuser
USER appuser

RUN printf '\\documentclass{article}\\begin{document}warmup\\end{document}' > /tmp/warmup.tex \
    && tectonic /tmp/warmup.tex \
    && rm -f /tmp/warmup.tex /tmp/warmup.pdf

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
