# artifacts

PR #2 writes one artifact:
- `sensitive_field_trace.json`

The trace includes:
- input and policy paths
- output directory and optional sheet argument
- dataset metadata (file/sheet/shape/column names)
- policy metadata (policy name/version, review levels, categories, overrides)
- status set to `intake_and_policy_loaded`

This artifact records deterministic intake evidence for human review workflows.
