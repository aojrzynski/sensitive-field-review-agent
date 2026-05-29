# Artifacts

Sensitive Field Review Agent writes review artifacts to the selected `--output-dir`. The deterministic artifacts are always written when the run succeeds. LLM artifacts are written when `--llm-review` is requested.

The artifacts are designed to support review without storing raw dataset rows in profile, signal, review, or LLM payload outputs.

## Summary table

| Artifact | When written | Primary audience | Raw values? | Purpose |
| --- | --- | --- | --- | --- |
| `sensitive_field_trace.json` | Every successful run | Reviewer, developer, auditor | File paths and column names, not raw rows | Records run metadata and artifact paths |
| `sensitive_field_profile.json` | Every successful run | Reviewer, developer | No raw rows; redacted example shapes only | Shows safe structural field profiles |
| `sensitive_field_signals.json` | Every successful run | Reviewer, developer | No raw rows | Shows deterministic field signals |
| `sensitive_field_results.json` | Every successful run | Reviewer, developer, automation | No raw rows | Shows structured deterministic review suggestions |
| `sensitive_field_findings.csv` | Every successful run | Reviewer, spreadsheet workflow | No raw rows | Provides a flat triage table |
| `sensitive_field_review_report.md` | Every successful run | Human reviewer | No raw rows | Provides a readable deterministic review report |
| `llm_safe_field_summary.json` | When `--llm-review` is requested | Reviewer, developer | No raw rows | Shows the exact safe deterministic payload for the LLM stage |
| `llm_field_review.json` | When `--llm-review` is requested | Reviewer, developer, automation | No raw rows | Shows structured completed, skipped, or fallback LLM output |
| `llm_field_review.md` | When `--llm-review` is requested | Human reviewer | No raw rows | Provides readable advisory LLM review notes |

## `sensitive_field_trace.json`

What it contains:

- input path, policy path, output directory, and optional sheet argument
- `llm_review_requested`
- `llm_review_status` such as `not_requested`, `skipped_missing_api_key`, `completed`, or fallback status
- dataset metadata including file name, extension, sheet name, shape, and column names
- policy metadata including policy name, version, review levels, categories, and overrides
- paths for deterministic and optional LLM artifacts
- final run status

Who it is for:

- reviewers who need run context
- developers debugging a workflow
- anyone comparing artifact sets across runs

Raw values:

- It records file paths, file metadata, and column names. It does not contain raw dataset rows.

How it supports review:

- It makes the run traceable and connects the input, policy, and generated artifacts.

## `sensitive_field_profile.json`

What it contains:

- dataset row and column counts
- one safe profile per field
- null, non-null, and distinct metrics
- inferred physical type such as string, number, boolean, datetime, or unknown
- string length summaries where applicable
- redacted example shapes

Who it is for:

- reviewers who want to understand field structure
- developers checking type inference and profile behavior

Raw values:

- It should not contain raw rows. Examples are redacted structural shapes.

How it supports review:

- It explains what each field looks like structurally without exposing the underlying values.

## `sensitive_field_signals.json`

What it contains:

- deterministic field-level signals
- pattern-family evidence such as aggregate counts, ratios, and thresholds
- column-name keyword evidence from the policy
- field-level signal summaries

Who it is for:

- reviewers who want to understand why a field was surfaced
- developers checking detector behavior

Raw values:

- It should not contain raw dataset values or row-level examples.

How it supports review:

- It provides the deterministic evidence used by the review engine.

## `sensitive_field_results.json`

What it contains:

- structured deterministic review suggestions by field
- `review_required`
- suggested policy category
- suggested review level
- confidence
- evidence summary
- supporting signals
- reviewer questions
- decision authority note

Who it is for:

- reviewers who want detailed structured output
- automation that needs JSON rather than Markdown or CSV

Raw values:

- It should not contain raw rows.

How it supports review:

- It connects deterministic evidence to suggested field-level triage outcomes.

## `sensitive_field_findings.csv`

What it contains:

- one row per field
- `column_name`
- `review_required`
- `suggested_policy_category`
- `suggested_review_level`
- `confidence`
- `evidence_summary`

Who it is for:

- reviewers who prefer spreadsheet-style review
- teams that want to sort, filter, or annotate findings outside the tool

Raw values:

- It should not contain raw dataset rows.

How it supports review:

- It gives a compact triage table that can be shared with reviewers.

## `sensitive_field_review_report.md`

What it contains:

- authority boundary
- input and policy file names
- row and column counts
- summary counts
- fields that may require review
- evidence summaries
- fields with no configured deterministic signals
- decision note

Who it is for:

- human reviewers reading the run output in GitHub, a terminal, or a Markdown viewer

Raw values:

- It should not contain raw dataset rows.

How it supports review:

- It provides a readable entry point before reviewers inspect JSON or CSV artifacts.

## `llm_safe_field_summary.json`

What it contains:

- the exact safe deterministic payload prepared for the LLM stage
- policy name and version
- authority note
- row and column counts
- field summaries
- deterministic review suggestions and evidence summaries
- aggregate signal and profile summaries
- reviewer questions
- decision authority notes

Who it is for:

- reviewers who want to confirm what would be sent to the LLM
- developers debugging the optional LLM stage

Raw values:

- It should not contain raw rows, raw matched values, or full local filesystem paths.

How it supports review:

- It makes the LLM boundary inspectable before trusting any advisory output.

## `llm_field_review.json`

What it contains:

- `llm_review_status`
- authority note
- field-level advisory notes when completed
- skipped/fallback status when the LLM stage does not run
- error category for supported fallback cases

Who it is for:

- reviewers who want structured advisory notes
- developers and automation checking whether the optional LLM stage completed or skipped

Raw values:

- It should not contain raw rows.

How it supports review:

- It records advisory output separately from deterministic review results.

## `llm_field_review.md`

What it contains:

- active advisory LLM review status
- authority boundary
- reminder that deterministic outputs remain authoritative evidence
- reminder that a human reviewer makes final decisions
- readable field-level advisory notes when completed

Who it is for:

- human reviewers who want a readable LLM-stage summary

Raw values:

- It should not contain raw rows.

How it supports review:

- It presents optional LLM notes without changing the deterministic review artifacts.

## Review boundary

All artifacts support field-level triage. They do not provide legal or compliance verdicts, and they do not replace human review.
