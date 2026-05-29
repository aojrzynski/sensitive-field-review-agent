# Architecture

Sensitive Field Review Agent is a deterministic-first review workflow for tabular files. The default path runs locally and does not require an LLM or API key.

```text
Dataset intake
  -> Policy loading
  -> Safe profiling
  -> Deterministic signal generation
  -> Deterministic review suggestion generation
  -> Artifact writing
  -> Optional active LLM review over safe deterministic evidence
```

## 1. Dataset intake

The CLI accepts an input dataset path and optional Excel sheet name.

Supported input formats:

- CSV (`.csv`)
- Excel workbook (`.xlsx`)
- macro-enabled Excel workbook (`.xlsm`)

The intake stage validates that the file exists, that the extension is supported, that a requested Excel sheet exists, and that the loaded dataset has rows and columns.

The stage records dataset metadata such as file name, extension, sheet name, row count, column count, and column names.

## 2. Policy loading

The policy loader reads a human-authored YAML policy. The policy defines the review vocabulary used by the deterministic workflow, including:

- policy name and version
- review levels
- policy categories
- field-name keywords
- pattern families
- reviewer questions
- redaction settings
- optional field overrides

The policy is an explicit workflow input, not hidden prompt text. Policy metadata is recorded in the trace artifact.

## 3. Safe profiling

The profiling stage creates safe structural summaries for each field. It computes metrics such as:

- null and non-null counts
- null ratio and distinct ratio
- inferred physical type
- string length summaries
- redacted example shapes

The profile is designed to support review without exposing raw dataset rows.

## 4. Deterministic signal generation

The signal stage generates deterministic field evidence from two main sources:

- policy keywords that match column names
- configured pattern-family detectors that evaluate field values and return aggregate evidence

Signals are written as explainable summaries. They are intended to show why a field may need review without storing raw matched values.

## 5. Deterministic review suggestion generation

The review engine combines the policy, profile, signals, and overrides to produce field-level triage suggestions.

For each field, the deterministic review output can include:

- whether review is suggested
- suggested policy category
- suggested review level
- confidence
- evidence summary
- supporting signals
- reviewer questions
- decision authority note

These are review suggestions, not final decisions.

## 6. Artifact writing

A successful deterministic run writes:

- `sensitive_field_trace.json`
- `sensitive_field_profile.json`
- `sensitive_field_signals.json`
- `sensitive_field_results.json`
- `sensitive_field_findings.csv`
- `sensitive_field_review_report.md`

The trace artifact preserves run metadata, input and policy metadata, artifact paths, and LLM status metadata.

## 7. Optional active LLM review over safe deterministic evidence

The LLM path is requested explicitly with `--llm-review`. It is not part of the default deterministic path.

When requested, the workflow builds `llm_safe_field_summary.json`, a safe deterministic evidence payload. The payload includes review suggestions, evidence summaries, safe profile summaries, signal summaries, reviewer questions, and authority notes. It does not include raw dataset rows.

If `OPENAI_API_KEY` is missing, the LLM stage is skipped and fallback artifacts are written. The command exits 0 after deterministic artifacts are generated.

If an API key and the optional LLM dependency are available, the active advisory LLM review can produce:

- `llm_field_review.json`
- `llm_field_review.md`

The LLM output does not alter deterministic review results. It is advisory and non-authoritative.

## Deterministic path is the authority base

The deterministic artifacts are the evidence base for the workflow. The optional LLM stage can help phrase ambiguity, suggest reviewer questions, and summarize limitations, but it does not decide final handling.

A human reviewer makes final decisions.
