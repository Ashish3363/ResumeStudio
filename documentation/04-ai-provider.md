# AI Provider Abstraction

The system is **not** coupled to Gemini. All AI access goes through one interface;
`GeminiProvider` is the only implementation in MVP. Swapping to OpenAI/Claude later
touches only the `ai/` module — business logic is unaffected.

## Interface
```python
class AIProvider(Protocol):
    def parse_resume(text: str) -> ResumeData
    def analyze_jd(jd_text: str) -> JDAnalysis
    def suggest_improvements(resume: ResumeData, jd: JDAnalysis) -> Suggestions
    def optimize_content(resume: ResumeData, jd: JDAnalysis, verified_skills) -> ResumeData
```

## Rules
- **Structured output only.** Use Gemini's JSON-schema / structured-output mode bound to the
  Pydantic schemas. Never parse free-text JSON out of a prose response.
- **Content only.** The AI returns `ResumeData` / `JDAnalysis` — never LaTeX, never layout.
- **Truth policy in prompts AND data.** Prompts forbid inventing content; the generator
  additionally drops any skill with `verified = false`, so a prompt failure can't leak fabricated skills.
- **Determinism boundary.** The match *score* is computed in code (`matching/`), not by the LLM.
  The LLM only writes qualitative suggestions.

## Module
- `ai/provider.py` — the `AIProvider` Protocol
- `ai/gemini.py` — `GeminiProvider`
- `ai/prompts/` — versioned prompt templates per task

## Config
Gemini API key supplied via environment (`.env`), never committed.
