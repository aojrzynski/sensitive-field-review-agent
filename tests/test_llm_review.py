import json

import pandas as pd

from sensitive_field_review_agent.llm_review import build_safe_payload, write_llm_artifacts
from sensitive_field_review_agent.policy_loader import load_policy
from sensitive_field_review_agent.profiling import profile_dataset
from sensitive_field_review_agent.review_engine import generate_dataset_review
from sensitive_field_review_agent.signals import generate_dataset_signals

RAW_VALUES = [
    "Alice Example",
    "alice@example.com",
    "07111 000001",
    "SW1A 1AA",
    "10 Demo Street",
    "sk_live_1234567890abcdef",
    "12345678",
]


def _sample_payload():
    policy = load_policy("config/examples/sensitive_field_policy.yaml")
    df = pd.DataFrame({
        "name": ["Alice Example"],
        "email": ["alice@example.com"],
        "phone": ["07111 000001"],
        "postcode": ["SW1A 1AA"],
        "address": ["10 Demo Street"],
        "token": ["sk_live_1234567890abcdef"],
        "account_number": ["12345678"],
    })
    profile = profile_dataset(df, 2)
    signals = generate_dataset_signals(df, policy)
    review = generate_dataset_review(policy, profile, signals)
    return build_safe_payload(review, profile, signals)


def test_safe_payload_contains_deterministic_review_info_and_no_raw_values():
    payload = _sample_payload()
    assert payload["policy_name"]
    assert payload["fields"]
    rendered = json.dumps(payload)
    for raw in RAW_VALUES:
        assert raw not in rendered


def test_markdown_and_json_artifacts_bounded_and_no_banned_terms(tmp_path):
    payload = _sample_payload()
    llm_result = {
        "llm_review_status": "completed",
        "authority_note": "Bounded non-authoritative review stage.",
        "field_reviews": [
            {
                "column_name": "email",
                "review_note": "This may require review.",
                "ambiguity_note": "Deterministic evidence is limited because only one row is available.",
                "suggested_reviewer_questions": ["What is expected business use?"],
                "evidence_limitations": ["Small sample size."],
            }
        ],
    }
    paths = write_llm_artifacts(tmp_path, payload, llm_result)
    for p in paths.values():
        assert (tmp_path / p.split('/')[-1]).exists()

    rendered = (tmp_path / "llm_field_review.md").read_text(encoding="utf-8").lower()
    assert "deterministic outputs remain authoritative evidence" in rendered
    assert "human reviewer makes final decisions" in rendered
    for banned in ["gdpr", "pii", "compliant", "non-compliant", "safe to share", "detected sensitive data"]:
        assert banned not in rendered
