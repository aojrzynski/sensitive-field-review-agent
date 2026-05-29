# Roadmap

This roadmap describes the current portfolio state and possible future improvements. It is not a promise of production support.

## Completed

- Initial Python project scaffold
- CSV/XLSX/XLSM dataset intake
- YAML policy loading with structural validation
- Safe deterministic field profiling
- Deterministic field signals from column-name keywords and pattern families
- Deterministic review suggestion generation
- JSON, CSV, and Markdown review artifacts
- Active advisory LLM review over safe deterministic evidence
- Skipped/fallback LLM artifacts when `--llm-review` is requested without `OPENAI_API_KEY`
- Manual-QA hardening for CLI error messages, profiling inference, warning noise, and evidence-summary priority
- Test coverage for core workflow behavior

## Possible future improvements

- Richer synthetic sample datasets
- Additional explainable pattern families
- Configurable report templates
- Policy authoring helper
- Stronger Excel and multi-sheet workflows
- Packaged CLI entrypoint examples in documentation
- More realistic demo scenarios
- Additional documentation validation checks

## Non-goals

- Legal or compliance verdicting
- Replacing human review
- Sending raw datasets to LLMs
- Making the LLM the authority layer
- Claiming exhaustive field classification
- Hiding policy decisions inside prompts
