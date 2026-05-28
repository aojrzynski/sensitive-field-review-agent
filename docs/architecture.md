# architecture

PR #3 adds deterministic profiling on top of intake + policy loading.

Current runtime flow:
- Parse CLI arguments.
- Load input dataset (CSV/XLSX/XLSM) with deterministic validation.
- Load YAML sensitive-field policy with structural validation.
- Generate deterministic safe field profiles from the dataset.
- Write `sensitive_field_profile.json`.
- Write `sensitive_field_trace.json` with dataset metadata, policy metadata, and profile artifact metadata.

Boundary reminders:
- This stage supports field-level triage setup only.
- It does not detect or classify sensitive fields yet.
- It does not provide legal/compliance verdicts.
- It does not call an LLM yet.
- Human reviewers make final decisions.
