# PDF Generation

**Scope:** MVP

## Summary
High-quality, Overleaf-grade PDFs via **LaTeX**, compiled with **Tectonic** inside Docker.
The AI never writes LaTeX. The pipeline:
```
Resume JSON → LaTeX Template Engine → Tectonic compile → PDF
```

## Template engine
- One universal **ATS-friendly** template (professional, minimal, clean, single-column).
- Resume JSON → LaTeX via Jinja2 with **LaTeX-safe escaping**.
- Renders only sections listed in `section_order`, in that order.
- Modular design so additional templates can be added later (Phase 2).

## Compile service (`pdf/`)
- Compiler: **Tectonic** (single binary; fetches/caches packages on demand).
- Output stored in object storage; `pdf_url` saved on the `resumes` row when the user saves.

## Security (mandatory — user text flows into a compiler)
- **shell-escape disabled.**
- Compile in an **isolated temp dir** with a **hard timeout**.
- **Escape all LaTeX special characters** (`& % $ # _ { } ~ ^ \`) on every injected field.
- Capture compile errors instead of leaking raw compiler output to the user.

## ATS verification
Confirm the compiled PDF has **selectable text** (copy text out of it), single-column layout,
and standard fonts — these determine real ATS parseability.

## Notes
- Tectonic chosen over full TeXLive (~4–5 GB) to keep the Docker image small.
- Compile + AI generation run synchronously in MVP; structured to move to background jobs later.
