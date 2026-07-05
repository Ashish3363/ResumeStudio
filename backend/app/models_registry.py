# Model registry — the single place that imports every feature's SQLAlchemy models.
#
# Importing this module registers all tables on Base.metadata. Alembic's env.py
# imports it so `--autogenerate` sees the full schema. Add one line here whenever
# a new feature introduces a model. (Models themselves live in their feature
# folder, e.g. app/users/models.py — this file only collects them.)

from app.database import Base  # noqa: F401  (re-exported so callers can grab metadata here)
from app.users.models import CareerProfile, User  # noqa: F401
from app.jd.models import JobDescription  # noqa: F401
from app.resumes.models import Resume  # noqa: F401

__all__ = ["Base", "User", "CareerProfile", "JobDescription", "Resume"]
