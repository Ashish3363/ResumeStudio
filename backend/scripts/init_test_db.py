"""
scripts/init_test_db.py
========================

Prepare the end-to-end test database. Invoked by Playwright's global setup with
DATABASE_URL pointing at the dedicated *_test database.

Steps:
  1. Create the test database if it doesn't exist (connects to the maintenance
     `postgres` DB to issue CREATE DATABASE).
  2. Create all tables from Base.metadata.
  3. TRUNCATE every table so each test run starts from a clean slate.

This keeps E2E runs fully isolated from the dev database.
"""

import os
import sys

# Ensure the backend root (this file's parent's parent) is importable as `app`,
# regardless of the current working directory the script is launched from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg
from sqlalchemy import create_engine, text

url = os.environ["DATABASE_URL"]  # e.g. postgresql+psycopg://postgres:root@localhost:5432/resumeStudio_test
base, name = url.rsplit("/", 1)
admin_dsn = f"{base}/postgres".replace("+psycopg", "")  # libpq DSN for the maintenance DB

# 1) Ensure the test database exists.
with psycopg.connect(admin_dsn, autocommit=True) as conn:
    exists = conn.execute("SELECT 1 FROM pg_database WHERE datname=%s", (name,)).fetchone()
    if exists:
        print(f"database {name} already exists")
    else:
        conn.execute(f'CREATE DATABASE "{name}"')
        print(f"created database {name}")

# 2) + 3) Create the schema and wipe it clean.
# Importing the registry pulls every model onto Base.metadata.
import app.models_registry as reg  # noqa: E402

engine = create_engine(url, future=True)
reg.Base.metadata.create_all(engine)
with engine.begin() as c:
    c.execute(
        text("TRUNCATE users, career_profiles, job_descriptions, resumes RESTART IDENTITY CASCADE")
    )
engine.dispose()
print("schema ready + tables truncated")
