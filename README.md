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
- trace artifact output with dataset and policy metadata
- tests and CI wiring for iterative development

## Why this is an agent
The tool acts as an agent by orchestrating multiple steps in a review workflow:
- accepts review inputs (dataset + policy)
- executes deterministic workflow stages
- records review trace artifacts
- optionally uses an LLM layer in a bounded, non-authoritative role

This PR adds a foundation layer only; detection/classification logic is intentionally deferred.

## Quick start
```bash
python -m pip install -e ".[dev]"
python -m sensitive_field_review_agent.cli --help
```

## Example commands
Deterministic intake run:

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.csv \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_sensitive_review
```

Optional LLM review mode (future behavior will be expanded):

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.csv \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_sensitive_review_llm \
  --llm-review
```

If `--llm-review` is requested without `OPENAI_API_KEY`, the intended long-term behavior is to continue and write deterministic fallback output. For PR #1, this is documented but not fully implemented.

## Output artifacts
The current version writes:
- `sensitive_field_trace.json`: intake trace with input metadata, policy metadata, and status.

Future PRs will add detection, triage evidence, and richer review artifacts.

## Authority boundary
- Deterministic signal extraction provides evidence.
- Policy configuration provides human-authored review criteria.
- Review/classification metadata supports triage and follow-up.
- Optional LLM output can assist wording and bounded semantic review.
- Human reviewers make final decisions.
- LLM output is never the source of truth.

Example wording for early review:
"This field appears likely to contain personal contact information and should be reviewed before sharing."

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

## Limitations and non-goals
- This scaffold does not implement full detection logic yet.
- It does not provide legal or regulatory verdicts.
- It does not replace human review decisions.
- It does not treat LLM output as authoritative evidence.

## Further reading
See the `docs/` directory for architecture notes, artifacts, roadmap, and design principles.
