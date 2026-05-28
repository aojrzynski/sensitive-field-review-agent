# Sensitive Field Review Agent

## Short description
Sensitive Field Review Agent is an early-stage Python tool for deterministic intake of tabular datasets and policy configuration to support sensitive-field triage workflows.

## Why this exists
Teams regularly share CSV and spreadsheet data across analytics, engineering, and vendor workflows. A lightweight review step helps identify columns that may need additional handling before data is shared.

This project focuses on making that review process explicit, repeatable, and auditable.

## Why not just ask an LLM?
An LLM can help with review interpretation, but it should not be the source of truth for data review decisions. Deterministic checks and clear policy configuration provide traceable evidence. Human reviewers still decide what to do.

## What this project demonstrates
The current implementation demonstrates:
- deterministic intake for CSV/XLSX/XLSM datasets
- YAML policy loading with structural validation
- deterministic safe field profiling (structural summaries only)
- deterministic field-signal extraction and review suggestions
- optional active LLM review over safe deterministic evidence when `--llm-review` is requested
- trace + profile + signals + deterministic review artifact output with dataset and policy metadata
- tests and CI wiring for iterative development

## Why this is an agent
The tool acts as an agent by orchestrating multiple steps in a review workflow:
- accepts review inputs (dataset + policy)
- executes deterministic workflow stages by default
- records review trace artifacts
- optionally requests active LLM review over safe/redacted deterministic summaries

This implementation includes deterministic profiling, deterministic field-signal extraction, deterministic review suggestions, and an optional bounded review assistant stage. It does not make legal or regulatory verdicts, and human reviewer makes the final decision.

## Quick start
```bash
python -m pip install -e ".[dev]"
python -m sensitive_field_review_agent.cli --help
```

## Example commands
Deterministic intake + profiling + signal extraction + review artifact run:

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.csv \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_sensitive_review
```

By default, the deterministic run makes no LLM call and does not require an API key.

Active LLM review over safe deterministic evidence:

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.csv \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_sensitive_review_llm \
  --llm-review
```

The `--llm-review` flag requests the active advisory LLM review stage. If `OPENAI_API_KEY` is not configured, the workflow still exits 0 after deterministic artifacts are generated and writes skipped/fallback LLM artifacts. If an API key and client dependency are configured, the LLM consumes only safe deterministic evidence: deterministic review results, safe profile summaries, deterministic signal summaries, policy metadata, reviewer questions, and authority boundary notes.

## Output artifacts
The deterministic workflow writes:
- `sensitive_field_trace.json`: intake, profiling, signals, review, and optional LLM trace metadata.
- `sensitive_field_profile.json`: deterministic safe field profile with redacted structural examples.
- `sensitive_field_signals.json`: deterministic field signals from pattern families and column-name keywords.
- `sensitive_field_results.json`: structured deterministic review suggestions by field.
- `sensitive_field_findings.csv`: flat findings table with suggested category/level and evidence summary.
- `sensitive_field_review_report.md`: human-readable report for review triage.

When `--llm-review` is requested, the workflow also writes:
- `llm_safe_field_summary.json`: the exact safe deterministic payload prepared for the LLM stage.
- `llm_field_review.json`: structured completed/skipped/fallback LLM review output.
- `llm_field_review.md`: human-readable advisory review notes and authority boundary.

The profile, signal, review, and LLM payload artifacts are intentionally value-safe and do not include raw row values.

## Authority boundary
- Deterministic signal extraction provides evidence.
- Policy configuration provides human-authored review criteria.
- This tool supports field-level triage, not final compliance decisions.
- It does not provide legal or regulatory verdicts.
- It does not determine protected-status labels for the dataset.
- The LLM stage must consume only safe/redacted summaries and deterministic evidence.
- The LLM must not receive raw dataset rows, override deterministic evidence, or decide whether data can be shared.
- Human reviewers make final decisions.

## Project structure
```text
.
├── docs/
├── src/sensitive_field_review_agent/
├── tests/
└── .github/workflows/
```

## Run tests
```bash
python -m pytest
```
