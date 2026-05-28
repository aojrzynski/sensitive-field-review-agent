# Sensitive Field Review Agent

## Short description
Sensitive Field Review Agent is an early-stage Python tool for deterministic intake of tabular datasets and policy configuration to support sensitive-field triage workflows.

## Why this exists
Teams regularly share CSV and spreadsheet data across analytics, engineering, and vendor workflows. A lightweight review step helps identify columns that may need additional handling before data is shared.

This project focuses on making that review process explicit, repeatable, and auditable.

## Why not just ask an LLM?
An LLM can help with wording and interpretation, but it should not be the source of truth for data review decisions. Deterministic checks and clear policy configuration provide traceable evidence. Human reviewers still decide what to do.

## What this project demonstrates
The current implementation demonstrates:
- deterministic intake for CSV/XLSX/XLSM datasets
- YAML policy loading with structural validation
- deterministic safe field profiling (structural summaries only)
- trace + profile artifact output with dataset and policy metadata
- tests and CI wiring for iterative development

## Why this is an agent
The tool acts as an agent by orchestrating multiple steps in a review workflow:
- accepts review inputs (dataset + policy)
- executes deterministic workflow stages
- records review trace artifacts
- prepares deterministic evidence and safe/redacted summaries for a future active LLM review stage

This implementation currently focuses on deterministic profiling only. It does not detect/classify sensitive fields yet.

## Quick start
```bash
python -m pip install -e ".[dev]"
python -m sensitive_field_review_agent.cli --help
```

## Example commands
Deterministic intake + profiling run:

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.csv \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_sensitive_review
```

Future active LLM review stage (not implemented yet):

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.csv \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_sensitive_review_llm \
  --llm-review
```

The `--llm-review` flag is currently accepted as workflow metadata only; no LLM calls are made at this stage. In a future stage, LLM review will consume only safe/redacted summaries plus deterministic evidence, must not receive raw dataset rows, must not override deterministic evidence, and must not make legal/compliance/GDPR verdicts.

## Output artifacts
The current version writes:
- `sensitive_field_trace.json`: intake and profiling trace with workflow metadata.
- `sensitive_field_profile.json`: deterministic safe field profile with redacted structural examples.

The profile artifact is intentionally value-safe and does not include raw row values.

## Authority boundary
- Deterministic signal extraction provides evidence.
- Policy configuration provides human-authored review criteria.
- This tool supports field-level triage, not final compliance decisions.
- It does not provide legal/regulatory verdicts.
- It does not determine GDPR/PII status.
- A future active LLM review stage must consume only safe/redacted summaries and deterministic evidence.
- The LLM must not receive raw dataset rows, override deterministic evidence, or make legal/compliance/GDPR verdicts.
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
