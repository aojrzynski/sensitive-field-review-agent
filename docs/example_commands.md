# example commands

Install and run:

```bash
python -m pip install -e ".[dev]"
python -m sensitive_field_review_agent.cli --help
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/customers_sensitive_review.csv \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/customers_sensitive_review
```

Expected artifacts:
- `outputs/customers_sensitive_review/sensitive_field_trace.json`
- `outputs/customers_sensitive_review/sensitive_field_profile.json`
- `outputs/customers_sensitive_review/sensitive_field_signals.json`
- `outputs/customers_sensitive_review/sensitive_field_results.json`
- `outputs/customers_sensitive_review/sensitive_field_findings.csv`
- `outputs/customers_sensitive_review/sensitive_field_review_report.md`

Excel input can include an explicit sheet:

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/workbook.xlsx \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/workbook_review \
  --sheet Customers
```


## Active LLM review over safe deterministic evidence

This project includes a bounded non-authoritative review assistant stage via `--llm-review`.
The LLM stage consumes only safe deterministic evidence (review results, profile summaries, signal summaries, and reviewer questions).
Deterministic outputs remain authoritative evidence, and human reviewers make final decisions.
The LLM stage provides advisory review notes and does not modify deterministic suggestions.
No legal/compliance verdicts are produced.
