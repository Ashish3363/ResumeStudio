"""
Resume JSON schema — the single source of truth for the entire platform.

This contract is shared by:
  - the AI provider (parse_resume / optimize_content output),
  - the database (`resume_versions.resume_json` JSONB column),
  - the structured editor forms on the frontend,
  - the LaTeX template engine.

Design rules baked into this schema:
  * Every Skill carries `verified` + `source`. The generator MUST refuse to emit any
    skill where `verified is False`. This enforces the truth policy IN DATA, not just
    in prompts. A "No Experience" answer means the skill is simply absent (never stored).
  * `section_order` lives inside the resume itself, so "section selection" and ATS
    reordering are just edits to this list — no separate state to track.
  * Dates are stored as free-form strings ("2023-01", "Jan 2023", "present") to avoid
    forcing a format the user/AI can't always satisfy. The template handles display.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #
class SkillLevel(str, Enum):
    """Maps directly to the missing-skill verification options the user picks."""

    EXPERT = "expert"
    INTERMEDIATE = "intermediate"
    BEGINNER = "beginner"
    LEARNING = "learning"  # "Currently Learning"
    # "No Experience" has no enum value on purpose: such skills are never added.


class SkillSource(str, Enum):
    """Where a skill came from. Drives the truth policy."""

    UPLOADED = "uploaded"  # extracted from the user's uploaded resume
    MANUAL = "manual"      # typed in by the user
    VERIFIED = "verified"  # confirmed via the missing-skill verification flow


class SectionKey(str, Enum):
    """Canonical identifiers for every selectable/orderable resume section."""

    SUMMARY = "summary"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    INTERNSHIPS = "internships"
    PROJECTS = "projects"
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    ACHIEVEMENTS = "achievements"
    LANGUAGES = "languages"
    AWARDS = "awards"
    PUBLICATIONS = "publications"
    VOLUNTEER = "volunteer"
    INTERESTS = "interests"


# --------------------------------------------------------------------------- #
# Leaf models
# --------------------------------------------------------------------------- #
class Link(BaseModel):
    label: str  # "GitHub", "LinkedIn", "Portfolio", ...
    url: str


class Basics(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    links: list[Link] = Field(default_factory=list)


class Skill(BaseModel):
    name: str
    level: SkillLevel = SkillLevel.INTERMEDIATE
    source: SkillSource = SkillSource.MANUAL
    verified: bool = False  # generator emits the skill ONLY when this is True


class ExperienceItem(BaseModel):
    company: str = ""
    role: str = ""
    location: str = ""
    start: str = ""          # free-form: "2023-01" / "Jan 2023"
    end: str = ""            # free-form: "present" allowed
    bullets: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    name: str = ""
    tech: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)
    link: str = ""


class EducationItem(BaseModel):
    school: str = ""
    degree: str = ""
    field: str = ""
    start: str = ""
    end: str = ""
    details: str = ""        # GPA, honors, relevant coursework, etc.


class CertificationItem(BaseModel):
    name: str = ""
    issuer: str = ""
    date: str = ""


class LanguageItem(BaseModel):
    name: str = ""
    proficiency: str = ""    # "Native", "Fluent", "Conversational", ...


# --------------------------------------------------------------------------- #
# Root model
# --------------------------------------------------------------------------- #
DEFAULT_SECTION_ORDER: list[SectionKey] = [
    SectionKey.SUMMARY,
    SectionKey.SKILLS,
    SectionKey.EXPERIENCE,
    SectionKey.PROJECTS,
    SectionKey.EDUCATION,
]


class ResumeData(BaseModel):
    """The complete structured resume. Stored verbatim as JSONB per version."""

    basics: Basics = Field(default_factory=Basics)
    summary: str = ""
    skills: list[Skill] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    internships: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    certifications: list[CertificationItem] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    languages: list[LanguageItem] = Field(default_factory=list)
    # Optional Phase-1 sections (present in schema so the template/editor are ready):
    awards: list[str] = Field(default_factory=list)
    publications: list[str] = Field(default_factory=list)
    volunteer: list[ExperienceItem] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)

    # Which sections render, and in what order. ATS reorder == editing this list.
    section_order: list[SectionKey] = Field(default_factory=lambda: list(DEFAULT_SECTION_ORDER))

    def verified_skills(self) -> list[Skill]:
        """The only skills the generator/template are allowed to emit."""
        return [s for s in self.skills if s.verified]
