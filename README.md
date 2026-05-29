# sensitive-field-review-agent

Sensitive Field Review Agent helps answer a practical question: "Which fields in this dataset may need human review before sharing, migration, analysis, or downstream use?"

Many tabular datasets contain columns that look harmless in isolation but may require review depending on context: names, emails, phone numbers, addresses, IDs, free text, financial-like fields, tokens, and secrets. This project does not make legal or compliance decisions. It creates deterministic evidence, suggested policy categories, suggested review levels, and reviewer prompts so a human reviewer can make final decisions.

## The problem

Teams often need to inspect unfamiliar CSV or spreadsheet extracts before they are copied into another system, sent to a vendor, used for analysis, or attached to a ticket. That review is often inconsistent, manual, and hard to audit.

Raw dataset rows should also not be casually pasted into an LLM. Reviewers need structured evidence that explains why a column may need attention, not a black-box guess over raw data.

Sensitive Field Review Agent is built around that boundary: deterministic evidence first, optional active advisory LLM review second, and human reviewer authority throughout.

## What this project does

The tool:

- loads CSV, XLSX, and XLSM datasets
- loads a human-authored YAML policy
- profiles fields with safe structural summaries
- generates deterministic field signals from pattern families and policy keywords
- produces deterministic review suggestions with evidence summaries
- optionally runs active advisory LLM review over safe deterministic evidence only
- writes traceable JSON, CSV, and Markdown artifacts for review

The deterministic workflow is the default path. It does not require an API key.

## Why deterministic evidence matters

Field review needs evidence that can be reproduced, inspected, and discussed. Deterministic signals are stable: the same input dataset and policy produce the same profile, signal, and review artifacts.

That matters because field-level triage should be auditable. A reviewer should be able to see which policy keyword matched, which pattern family produced evidence, and what suggested review level came from the configured policy.

LLM output can help with ambiguity and review wording, but it should not be the authority layer. In this project, deterministic outputs remain the evidence base.

## Why not just ask an LLM?

Raw rows may contain values that should not be sent to an LLM. Even when an LLM is useful, it should not decide truth for a field-level review workflow.

This repo separates the two roles:

- deterministic code profiles fields, generates signals, and creates review suggestions
- optional active advisory LLM review reads only safe deterministic evidence
- a human reviewer makes final decisions

The LLM stage can summarize ambiguity and suggest reviewer questions. It does not receive raw dataset rows, replace deterministic evidence, or make legal/compliance verdicts.

## What this project demonstrates

- local-first dataset intake
- policy-driven review criteria
- safe and redacted field profiling
- deterministic pattern and keyword signals
- deterministic review artifacts in JSON, CSV, and Markdown
- active advisory LLM review over safe deterministic evidence
- clear human-review authority boundary
- test-covered CLI behavior and artifact generation

## Why this is an agent

This is an agent because it orchestrates a multi-step review workflow:

```text
intake -> policy -> profile -> signals -> review suggestions -> optional LLM review
```

It does not perform open-ended autonomy. It runs a bounded workflow, keeps each stage traceable, and produces artifacts for a human reviewer. The optional LLM review is active because it is requested as part of the workflow and can produce advisory notes, but it is non-authoritative.

## Quick start

Install the project with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
python -m pytest -q
```

Optional LLM setup:

```bash
python -m pip install -e ".[dev,llm]"
```

`OPENAI_API_KEY` is not needed for deterministic runs. If `--llm-review` is requested without `OPENAI_API_KEY`, the command still writes skipped/fallback LLM artifacts and exits 0 after deterministic artifacts are generated. With `OPENAI_API_KEY` and the optional LLM dependency installed, active advisory LLM review can run over the safe deterministic evidence payload.

## Example commands

Deterministic CSV review:

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.csv \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_sensitive_review
```

LLM-requested review. This command works both without a key, where skipped/fallback LLM artifacts are written, and with a configured key, where active advisory LLM review can run:

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.csv \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_sensitive_review_llm \
  --llm-review
```

Excel review with an explicit sheet:

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.xlsx \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_excel_review \
  --sheet Customers
```

The Excel command assumes `sample_data/customers/customers_sensitive_review.xlsx` exists in the working copy.

## Output artifacts

Deterministic runs write:

- `sensitive_field_trace.json`: run metadata, input metadata, policy metadata, artifact paths, and optional LLM status metadata
- `sensitive_field_profile.json`: safe field profile summaries, inferred physical types, null/distinct metrics, and redacted example shapes
- `sensitive_field_signals.json`: deterministic pattern-family and column-name keyword signals
- `sensitive_field_results.json`: structured deterministic review suggestions by field
- `sensitive_field_findings.csv`: flat triage table with suggested category, suggested review level, confidence, and evidence summary
- `sensitive_field_review_report.md`: human-readable deterministic review report

When `--llm-review` is requested, the workflow also writes:

- `llm_safe_field_summary.json`: exact safe deterministic payload prepared for the LLM stage
- `llm_field_review.json`: structured completed, skipped, or fallback LLM review output
- `llm_field_review.md`: human-readable active advisory LLM review notes

The profile, signal, review, and LLM payload artifacts are designed to avoid raw row values.

## Authority boundary

- Deterministic outputs provide evidence and triage suggestions.
- The YAML policy is human-authored review criteria.
- Suggested policy category and suggested review level are not final decisions.
- LLM review is advisory and non-authoritative.
- No raw rows are sent to the LLM.
- A human reviewer decides final handling.
- The tool does not provide legal or compliance verdicts.

## Project structure

- `src/sensitive_field_review_agent/cli.py`: CLI orchestration and artifact writing
- `src/sensitive_field_review_agent/intake.py`: CSV/XLSX/XLSM dataset loading and validation
- `src/sensitive_field_review_agent/policy_loader.py`: YAML policy loading and structural validation
- `src/sensitive_field_review_agent/profiling.py`: safe deterministic field profiling
- `src/sensitive_field_review_agent/signals.py`: deterministic pattern-family and keyword signals
- `src/sensitive_field_review_agent/review_engine.py`: deterministic review suggestion generation
- `src/sensitive_field_review_agent/llm_review.py`: safe payload creation and optional active advisory LLM review
- `src/sensitive_field_review_agent/models.py`: dataclasses shared across workflow stages
- `config/examples/sensitive_field_policy.yaml`: example human-authored policy
- `sample_data/customers/customers_sensitive_review.csv`: synthetic customer dataset for demos and tests
- `docs/`: architecture, artifact, command, demo, design, and roadmap notes

## Run tests

```bash
python -m pytest -q
```

## Limitations and non-goals

- Not a legal or compliance decision tool.
- Not a replacement for human review.
- Not a raw-data LLM upload tool.
- Detectors are intentionally simple and explainable.
- Policy quality matters because the policy drives review criteria.
- The project is currently focused on tabular files.

## Further reading

- [Architecture](docs/architecture.md)
- [Design principles](docs/design_principles.md)
- [Artifacts](docs/artifacts.md)
- [Demo walkthrough](docs/demo_walkthrough.md)
- [Example commands](docs/example_commands.md)
- [Roadmap](docs/roadmap.md)
