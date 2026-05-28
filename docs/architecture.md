# architecture

The current implementation includes deterministic intake, policy loading, safe profiling, deterministic signal generation, and deterministic review suggestion generation.

Current runtime flow:
- Parse CLI arguments.
- Load input dataset (CSV/XLSX/XLSM) with deterministic validation.
- Load YAML sensitive-field policy with structural validation.
- Generate deterministic safe field profiles from the dataset.
- Generate deterministic field signals from policy keywords and pattern families.
- Generate deterministic review suggestions from policy + profile + signals + overrides.
- Write `sensitive_field_profile.json`.
- Write `sensitive_field_signals.json`.
- Write `sensitive_field_results.json`.
- Write `sensitive_field_findings.csv`.
- Write `sensitive_field_review_report.md`.
- Write `sensitive_field_trace.json` with dataset metadata, policy metadata, and artifact metadata.

Boundary reminders:
- These are suggested review outputs for human triage.
- They are not final decisions.
- They do not provide legal/compliance verdicts.
- They do not determine GDPR/PII status.
- They do not call an LLM yet.
- Human reviewers make final decisions.


## Active LLM review over safe deterministic evidence

This project includes a bounded non-authoritative review assistant stage via `--llm-review`.
The LLM stage consumes only safe deterministic evidence (review results, profile summaries, signal summaries, and reviewer questions).
Deterministic outputs remain authoritative evidence, and human reviewers make final decisions.
The LLM stage provides advisory review notes and does not modify deterministic suggestions.
No legal/compliance verdicts are produced.
