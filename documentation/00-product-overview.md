# Product Overview

## What it is
An AI-powered **Resume Tailoring Platform** (SaaS) that generates ATS-friendly,
industry-standard resumes tailored to a specific Job Description (JD). It behaves
like an **AI career coach**, not a text generator.

## Core principle — Truthful Optimization
The AI must **never fabricate** skills, experience, projects, certifications, or
achievements. Anything required by the JD but missing from the user's profile must be
**explicitly verified by the user** before it can appear in the resume.

A piece of information may appear in the resume only if it:
1. exists in the uploaded resume, **or**
2. was manually entered by the user, **or**
3. was explicitly verified by the user (missing-skill verification flow).

This rule is enforced **in data** (every skill carries a `verified` flag), not just in prompts.

## Primary workflow
1. User logs in.
2. User pastes a Job Description.
3. User uploads an existing resume **or** enters details manually.
4. AI extracts and structures the user's information.
5. AI analyzes the Job Description.
6. AI compares profile against the JD (match report).
7. AI asks the user to verify any missing skills.
8. AI generates an ATS-optimized resume (verified data only).
9. User edits via structured section forms (never LaTeX).
10. Backend regenerates LaTeX + PDF automatically.
11. User saves the resume to their profile (up to 10, FIFO), downloads the PDF, or renames it.

## Product philosophy
This is not "another resume builder." It is a **truthful, transparent, ATS-optimized
tailoring assistant** that shows the user exactly what changed and never invents content.
