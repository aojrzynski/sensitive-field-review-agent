# architecture

The current implementation adds deterministic profiling and deterministic field signals on top of intake + policy loading.

Current runtime flow:
- Parse CLI arguments.
- Load input dataset (CSV/XLSX/XLSM) with deterministic validation.
- Load YAML sensitive-field policy with structural validation.
- Generate deterministic safe field profiles from the dataset.
- Generate deterministic field signals from policy keywords and pattern families.
- Write `sensitive_field_profile.json`.
- Write `sensitive_field_signals.json`.
- Write `sensitive_field_trace.json` with dataset metadata, policy metadata, profile artifact metadata, and signal artifact metadata.

Boundary reminders:
- This stage supports field-level triage setup only.
- It does not create final review findings or final field classifications yet.
- It does not provide legal/compliance verdicts.
- It does not call an LLM yet.
- Human reviewers make final decisions.
