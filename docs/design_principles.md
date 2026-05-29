# Design principles

Sensitive Field Review Agent is designed for field-level triage of tabular datasets. The core idea is simple: create useful review evidence without turning the tool or the LLM into the final authority.

## Deterministic evidence first

The default workflow is deterministic. Dataset intake, profiling, signal generation, and review suggestion generation run without an LLM. The same dataset and policy should produce the same deterministic artifacts.

This makes the review easier to inspect. A human reviewer can see which field signals were generated, which policy category was suggested, and which review level was suggested.

## Human-authored policy

The YAML policy is review criteria written by a person. It defines categories, review levels, field-name keywords, pattern families, reviewer questions, and optional overrides.

The policy is not hidden inside a prompt. It is a versioned input to the workflow, and the trace artifact records policy metadata for the run.

## Safe summaries, not raw values

The profiling and signal artifacts are designed around safe summaries. They include structural metrics, inferred physical types, aggregate counts, ratios, pattern-family evidence, and redacted example shapes.

They should not include raw dataset rows. This keeps the workflow useful for triage while avoiding casual raw-data exposure in review artifacts or LLM prompts.

## Active but bounded LLM review

When `--llm-review` is requested, the LLM stage receives a safe deterministic evidence payload. It can produce advisory notes, ambiguity notes, and suggested reviewer questions.

The LLM stage is bounded:

- it does not receive raw rows
- it does not change deterministic review results
- it does not decide final handling
- it does not provide legal or compliance verdicts

If `OPENAI_API_KEY` is not configured, the workflow writes skipped/fallback LLM artifacts and exits 0 after deterministic artifacts are generated.

## Human reviewer authority

The human reviewer makes final decisions. The tool supports field-level triage by producing deterministic evidence, suggested policy categories, suggested review levels, and review prompts.

Suggested outputs are starting points for review, not final labels or approvals.

## Local-first execution

The deterministic workflow runs locally over local files. It can review CSV, XLSX, and XLSM input without network access or an API key.

The optional LLM path is explicitly requested with `--llm-review` and uses only the safe deterministic evidence payload.

## Traceable artifacts

Each run writes artifacts that separate the review stages:

- trace metadata
- safe profiling
- deterministic signals
- deterministic review suggestions
- human-readable report
- optional LLM payload and advisory review notes

This separation makes the workflow easier to debug, audit, and explain.

## Practical portfolio scope

The project intentionally uses explainable detectors and a compact synthetic dataset. The goal is to show a complete, test-covered review workflow with clear boundaries, not to claim exhaustive coverage of every possible field type or policy situation.
