import importlib.machinery
import json
import sys
import types

import pandas as pd

from sensitive_field_review_agent.llm_review import build_safe_payload, run_llm_review, write_llm_artifacts
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

BANNED_TERMS = [
    "gdpr",
    "pii",
    "compliant",
    "non-compliant",
    "safe to share",
    "not safe to share",
    "detected sensitive data",
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
    for artifact_path in paths.values():
        assert (tmp_path / artifact_path.split('/')[-1]).exists()

    rendered = (tmp_path / "llm_field_review.md").read_text(encoding="utf-8").lower()
    assert "deterministic outputs remain authoritative evidence" in rendered
    assert "human reviewer makes final decisions" in rendered
    for banned in BANNED_TERMS:
        assert banned not in rendered


def test_llm_output_sanitizer_applies_to_json_and_markdown(tmp_path):
    payload = _sample_payload()
    llm_result = {
        "llm_review_status": "completed",
        "authority_note": "No GDPR or PII verdict is being made.",
        "field_reviews": [
            {
                "column_name": "email",
                "review_note": "This is PII and detected sensitive data.",
                "ambiguity_note": "It may be GDPR relevant but not compliant to decide here.",
                "suggested_reviewer_questions": ["Is this safe to share with a vendor?"],
                "evidence_limitations": ["Cannot say it is not safe to share or non-compliant."],
            }
        ],
    }

    write_llm_artifacts(tmp_path, payload, llm_result)
    rendered_json = (tmp_path / "llm_field_review.json").read_text(encoding="utf-8").lower()
    rendered_markdown = (tmp_path / "llm_field_review.md").read_text(encoding="utf-8").lower()

    for rendered in [rendered_json, rendered_markdown]:
        for banned in BANNED_TERMS:
            assert banned not in rendered


def test_run_llm_review_parses_mocked_success(monkeypatch):
    payload = _sample_payload()
    output = {
        "authority_note": "Advisory only.",
        "field_reviews": [
            {
                "column_name": "email",
                "review_note": "The deterministic evidence suggests this field may require review.",
                "ambiguity_note": "Evidence is limited because this is a summary.",
                "suggested_reviewer_questions": ["What is the intended field use?"],
                "evidence_limitations": ["No raw rows were provided."],
            }
        ],
    }

    class FakeResponse:
        output_text = json.dumps(output)

    class FakeResponses:
        def create(self, model, input):
            assert model == "test-model"
            assert input
            return FakeResponse()

    class FakeOpenAI:
        def __init__(self, api_key):
            assert api_key == "test-key"
            self.responses = FakeResponses()

    fake_openai = types.ModuleType("openai")
    fake_openai.__spec__ = importlib.machinery.ModuleSpec("openai", loader=None)
    fake_openai.OpenAI = FakeOpenAI

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    result = run_llm_review(payload, "test-model")

    assert result["llm_review_status"] == "completed"
    assert result["field_reviews"][0]["column_name"] == "email"
    assert "deterministic evidence suggests" in result["field_reviews"][0]["review_note"]
