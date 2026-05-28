# artifacts

## Deterministic artifacts
The deterministic workflow writes these artifacts on every successful run:
- `sensitive_field_trace.json`
- `sensitive_field_profile.json`
- `sensitive_field_signals.json`
- `sensitive_field_results.json`
- `sensitive_field_findings.csv`
- `sensitive_field_review_report.md`

## Optional LLM artifacts
When `--llm-review` is requested, the workflow also writes:
- `llm_safe_field_summary.json`
- `llm_field_review.json`
- `llm_field_review.md`

If no `OPENAI_API_KEY` is configured, these LLM artifacts still exist with a skipped/fallback status, and deterministic artifacts remain available.

## sensitive_field_trace.json
Includes:
- input and policy paths
- output directory and optional sheet argument
- `llm_review_requested`
- `llm_review_status` (`not_requested`, `skipped_missing_api_key`, `completed`, or `failed_fallback`)
- dataset metadata (file/sheet/shape/column names)
- policy metadata (policy name/version, review levels, categories, overrides)
- profile artifact metadata (`profile_artifacts.field_profile_path`)
- signal artifact metadata (`signal_artifacts.field_signals_path`)
- review artifact metadata:
  - `review_artifacts.results_path`
  - `review_artifacts.findings_csv_path`
  - `review_artifacts.review_report_path`
- LLM artifact metadata when `--llm-review` is requested:
  - `llm_artifacts.safe_field_summary_path`
  - `llm_artifacts.field_review_json_path`
  - `llm_artifacts.field_review_markdown_path`
- status set to `review_artifacts_generated`

## sensitive_field_profile.json
Includes deterministic safe field profile data:
- dataset-level metadata (`row_count`, `column_count`)
- one profile per field (`field_profiles`)
- structural statistics (null/non-null/distinct metrics)
- inferred physical type (string/number/boolean/datetime/unknown)
- string length aggregates
- safe/redacted example shapes only (no raw values)

## sensitive_field_signals.json
Includes deterministic field-level signal data:
- dataset-level metadata (`row_count`, `column_count`)
- one entry per field (`fields`)
- per-field `signals` containing pattern-family signals and column-name keyword signals
- aggregate-only evidence (counts/ratios/thresholds or matched policy keyword)
- no raw dataset values and no row-level examples

## sensitive_field_results.json
Includes structured deterministic review suggestions:
- field-level suggested policy category
- suggested review level
- confidence and review-required flag
- deterministic evidence summaries and supporting signals
- reviewer questions and authority boundary note

## sensitive_field_findings.csv
Includes a flat review table for triage:
- `column_name`
- `review_required`
- `suggested_policy_category`
- `suggested_review_level`
- `confidence`
- `evidence_summary`

## sensitive_field_review_report.md
Includes a human-readable triage summary:
- authority boundary
- input/policy file names
- summary counts
- fields that may require review
- fields with no configured deterministic signals

## llm_safe_field_summary.json
Includes the exact safe deterministic payload prepared for the LLM stage:
- policy name/version and authority note
- row/column counts
- one safe field summary per column
- deterministic review suggestions and evidence summaries
- aggregate signal/profile summaries
- reviewer questions and decision authority notes

It does not include raw dataset rows, raw matched values, or full local filesystem paths.

## llm_field_review.json
Includes structured LLM stage output when `--llm-review` is requested:
- `llm_review_status`
- authority note
- field-level advisory review notes when completed
- skipped/fallback status when the LLM stage is unavailable

## llm_field_review.md
Includes human-readable advisory review notes when `--llm-review` is requested:
- authority boundary
- reminder that deterministic outputs remain authoritative evidence
- reminder that human reviewers make final decisions
- completed, skipped, or fallback status

All review outputs are triage suggestions for human review. They are not legal or regulatory verdicts, and they do not make final decisions.
