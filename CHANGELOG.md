# Changelog

## v1.0.0

Initial portfolio-ready release of Sensitive Field Review Agent.

### Added
- Local-first CSV/XLSX/XLSM dataset intake.
- Human-authored YAML policy loading and validation.
- Safe deterministic field profiling with redacted structural summaries.
- Deterministic field signals from policy keywords and pattern-family detectors.
- Deterministic review suggestions with JSON, CSV, and Markdown artifacts.
- Active advisory LLM review over safe deterministic evidence when requested.
- Skipped/fallback LLM artifacts when --llm-review is requested without OPENAI_API_KEY.
- Clean CLI error handling for expected user mistakes.
- Portfolio documentation, demo walkthrough, artifact guide, roadmap, and explanatory code comments.

### Boundaries
- No raw dataset rows are sent to the LLM.
- LLM output is advisory and non-authoritative.
- Human reviewers make final decisions.
- The tool supports field-level triage, not legal or compliance verdicting.
