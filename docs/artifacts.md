# artifacts

Current artifacts:
- `sensitive_field_trace.json`
- `sensitive_field_profile.json`
- `sensitive_field_signals.json`

## sensitive_field_trace.json
Includes:
- input and policy paths
- output directory and optional sheet argument
- llm review request metadata
- dataset metadata (file/sheet/shape/column names)
- policy metadata (policy name/version, review levels, categories, overrides)
- profile artifact metadata (`profile_artifacts.field_profile_path`)
- signal artifact metadata (`signal_artifacts.field_signals_path`)
- status set to `signals_generated`

## sensitive_field_profile.json
Includes deterministic safe field profile data:
- dataset-level metadata (`row_count`, `column_count`)
- one profile per field (`field_profiles`)
- structural statistics (null/non-null/distinct metrics)
- inferred physical type (string/number/boolean/datetime/unknown)
- string length aggregates
- safe/redacted example shapes only (no raw values)

This artifact is designed for downstream triage support. It does not classify fields, make legal/compliance verdicts, or determine GDPR/PII status.


## sensitive_field_signals.json
Includes deterministic field-level signal data:
- dataset-level metadata (`row_count`, `column_count`)
- one entry per field (`fields`)
- per-field `signals` containing pattern-family signals and column-name keyword signals
- aggregate-only evidence (counts/ratios/thresholds or matched policy keyword)
- no raw dataset values and no row-level examples

This artifact is evidence for downstream triage. It does not assign final categories, final review levels, or legal/compliance/GDPR/PII verdicts.
