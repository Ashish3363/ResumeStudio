"""
Job Description analysis schema.

Produced by `AIProvider.analyze_jd(jd_text)` and stored as
`job_descriptions.analysis_json` (JSONB). The matching module consumes this
to compute the deterministic match score and to find missing skills.

Note: the AI EXTRACTS structure from the JD here — it does not judge the user.
It must not invent requirements that aren't in the text.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class JDAnalysis(BaseModel):
    title: str = ""                                        # role title if stated
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)  # tools/platforms
    frameworks: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)     # programming languages
    soft_skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    experience_requirements: list[str] = Field(default_factory=list)  # e.g. "3+ years backend"
    responsibilities: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)      # ATS keywords to surface
    action_verbs: list[str] = Field(default_factory=list)  # verbs to favor in bullets

    def all_skill_terms(self) -> list[str]:
        """Flat, de-duplicated list of every skill-like term mentioned in the JD.

        Used by the matching module to diff against the resume's skills.
        Order preserved; case-insensitive de-dup.
        """
        seen: set[str] = set()
        out: list[str] = []
        for bucket in (
            self.required_skills,
            self.preferred_skills,
            self.technologies,
            self.frameworks,
            self.languages,
        ):
            for term in bucket:
                key = term.strip().lower()
                if key and key not in seen:
                    seen.add(key)
                    out.append(term.strip())
        return out
