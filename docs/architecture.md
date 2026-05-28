# architecture

The default implementation path is deterministic: intake, policy loading, safe profiling, deterministic signal generation, and deterministic review suggestion generation.

Default runtime flow:
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
- Write `sensitive_field_trace.json` with dataset metadata, policy metadata, artifact metadata, and LLM request/status metadata.

## Active LLM review over safe deterministic evidence

When `--llm-review` is passed, the CLI adds a bounded advisory LLM review stage after deterministic artifacts have been prepared:
- Build `llm_safe_field_summary.json` from deterministic review results, safe profile summaries, deterministic signal summaries, policy metadata, reviewer questions, and authority boundary notes.
- If `OPENAI_API_KEY` is missing, write skipped/fallback LLM artifacts and exit 0 after deterministic outputs are generated.
- If configured, call the LLM with only the safe deterministic payload.
- Write `llm_field_review.json` and `llm_field_review.md`.
- Update `sensitive_field_trace.json` with `llm_review_status` and `llm_artifacts` metadata.

The LLM output does not modify `sensitive_field_results.json`, `sensitive_field_findings.csv`, or `sensitive_field_review_report.md`. Deterministic review results remain the traceable evidence foundation.

Boundary reminders:
- These are suggested review outputs for human triage.
- They are not final decisions.
- They do not provide legal or regulatory verdicts.
- They do not determine protected-status labels for the dataset.
- The LLM stage is advisory and non-authoritative.
- Human reviewers make final decisions.
