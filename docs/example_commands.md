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

Excel input can include an explicit sheet:

```bash
python -m sensitive_field_review_agent.cli \
  --input sample_data/customers/workbook.xlsx \
  --policy config/examples/sensitive_field_policy.yaml \
  --output-dir outputs/workbook_review \
  --sheet Customers
```
