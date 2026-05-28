# artifacts

Current artifacts:
- `sensitive_field_trace.json`
- `sensitive_field_profile.json`

## sensitive_field_trace.json
Includes:
- input and policy paths
- output directory and optional sheet argument
- llm review request metadata
- dataset metadata (file/sheet/shape/column names)
- policy metadata (policy name/version, review levels, categories, overrides)
- profile artifact metadata (`profile_artifacts.field_profile_path`)
- status set to `profile_generated`

## sensitive_field_profile.json
Includes deterministic safe field profile data:
- dataset-level metadata (`row_count`, `column_count`)
- one profile per field (`field_profiles`)
- structural statistics (null/non-null/distinct metrics)
- inferred physical type (string/number/boolean/datetime/unknown)
- string length aggregates
- safe/redacted example shapes only (no raw values)

This artifact is designed for downstream triage support. It does not classify fields, make legal/compliance verdicts, or determine GDPR/PII status.
