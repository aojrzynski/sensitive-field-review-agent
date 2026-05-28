# architecture

PR #2 adds the intake-and-policy foundation layer.

Current runtime flow:
- Parse CLI arguments.
- Load input dataset (CSV/XLSX/XLSM) with deterministic validation.
- Load YAML sensitive-field policy with structural validation.
- Write a trace artifact with dataset and policy metadata.

Boundary reminders:
- This stage supports triage setup only.
- It does not detect or classify sensitive fields yet.
- Human reviewers make final decisions.
