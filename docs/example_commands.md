# Example commands

These commands assume they are run from the repository root.

## Setup

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Optional LLM dependency:

```bash
python -m pip install -e ".[dev,llm]"
```

## Run tests

```bash
python -m pytest -q
```

## Deterministic CSV example

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.csv \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_sensitive_review
```

Expected deterministic artifacts:

- `outputs/customers_sensitive_review/sensitive_field_trace.json`
- `outputs/customers_sensitive_review/sensitive_field_profile.json`
- `outputs/customers_sensitive_review/sensitive_field_signals.json`
- `outputs/customers_sensitive_review/sensitive_field_results.json`
- `outputs/customers_sensitive_review/sensitive_field_findings.csv`
- `outputs/customers_sensitive_review/sensitive_field_review_report.md`

This run does not require `OPENAI_API_KEY`.

## Excel sheet example

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.xlsx \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_excel_review \
  --sheet Customers
```

The command assumes `sample_data/customers/customers_sensitive_review.xlsx` exists and contains a sheet named `Customers`.

For `.xlsx` and `.xlsm` files, the CLI uses the first sheet when `--sheet` is omitted.

## LLM-requested example

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.csv \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_sensitive_review_llm \
  --llm-review
```

Expected additional artifacts when `--llm-review` is requested:

- `outputs/customers_sensitive_review_llm/llm_safe_field_summary.json`
- `outputs/customers_sensitive_review_llm/llm_field_review.json`
- `outputs/customers_sensitive_review_llm/llm_field_review.md`

If `OPENAI_API_KEY` is not configured, the command still exits 0 after deterministic artifacts are generated and writes skipped/fallback LLM artifacts.

With `OPENAI_API_KEY` configured and the optional LLM dependency installed, the active advisory LLM review can run over the safe deterministic evidence payload.

## Error examples

Expected user errors are shown as clean `Error:` messages without tracebacks.

### Missing file

```bash
python -m sensitive_field_review_agent.cli \
  --input missing.csv \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/missing_file
```

Example output:

```text
Error: Dataset file not found: missing.csv
```

### Unsupported extension

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.txt \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/unsupported_extension
```

Example output:

```text
Error: Unsupported dataset extension: .txt. Supported formats: .csv, .xlsx, .xlsm
```

### Wrong Excel sheet

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.xlsx \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/wrong_sheet \
  --sheet WrongSheet
```

Example output:

```text
Error: Sheet 'WrongSheet' not found in workbook. Available sheets: ['Customers']
```

The exact available sheet list depends on the workbook.
