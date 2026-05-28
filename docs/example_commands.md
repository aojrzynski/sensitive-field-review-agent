# example commands

Install and run:

```bash
python -m pip install -e ".[dev]"
python -m sensitive_field_review_agent.cli --help
```

Deterministic run:

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

Active LLM review over safe deterministic evidence:

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

Excel input can include an explicit sheet:

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/workbook.xlsx \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/workbook_review \
  --sheet Customers
```
