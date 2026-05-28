from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from sensitive_field_review_agent.models import DatasetProfile, DatasetReviewResult, DatasetSignals

DEFAULT_LLM_MODEL = "gpt-4.1-mini"
BANNED_TERMS = ["gdpr", "pii", "compliant", "non-compliant", "safe to share", "not safe to share", "detected sensitive data"]


def _signal_summary(signals: dict) -> list[dict]:
    out: list[dict] = []
    for signal in signals.get("signals", []):
        if not signal.get("matched"):
            continue
        evidence = signal.get("evidence", {})
        out.append(
            {
                "signal_type": signal.get("signal_type"),
                "signal_name": signal.get("signal_name"),
                "policy_category": signal.get("policy_category"),
                "evidence": {
                    "checked_count": evidence.get("checked_count"),
                    "matched_count": evidence.get("matched_count"),
                    "matched_ratio": evidence.get("matched_ratio"),
                    "threshold_met": evidence.get("threshold_met"),
                    "matched_keyword": evidence.get("matched_keyword"),
                },
                "notes": signal.get("notes"),
            }
        )
    return out


def build_safe_payload(review: DatasetReviewResult, profile: DatasetProfile, signals: DatasetSignals) -> dict:
    review_dict = asdict(review)
    profile_dict = asdict(profile)
    signals_dict = asdict(signals)
    profile_by_col = {f["column_name"]: f for f in profile_dict["field_profiles"]}
    signal_by_col = {f["column_name"]: f for f in signals_dict["fields"]}

    fields = []
    for rf in review_dict["fields"]:
        col = rf["column_name"]
        p = profile_by_col.get(col, {})
        fields.append(
            {
                "column_name": col,
                "suggested_policy_category": rf.get("suggested_policy_category"),
                "suggested_review_level": rf.get("suggested_review_level"),
                "confidence": rf.get("confidence"),
                "review_required": rf.get("review_required"),
                "evidence_summary": rf.get("evidence_summary"),
                "supporting_signals": [asig["summary"] for asig in rf.get("supporting_signals", [])],
                "signal_summaries": _signal_summary(signal_by_col.get(col, {})),
                "profile_summary": {
                    "inferred_physical_type": p.get("inferred_physical_type"),
                    "null_ratio": p.get("null_ratio"),
                    "distinct_ratio": p.get("distinct_ratio"),
                    "string_min_length": p.get("string_min_length"),
                    "string_max_length": p.get("string_max_length"),
                    "string_avg_length": p.get("string_avg_length"),
                },
                "reviewer_questions": rf.get("reviewer_questions", []),
                "decision_authority_note": rf.get("decision_authority_note", ""),
            }
        )

    return {
        "policy_name": review_dict["policy_name"],
        "policy_version": review_dict.get("policy_version"),
        "authority_note": review_dict.get("authority_note"),
        "row_count": review_dict["row_count"],
        "column_count": review_dict["column_count"],
        "fields": fields,
    }


def _messages(payload: dict) -> list[dict]:
    instruction = (
        "You are a review assistant for deterministic field triage. "
        "Use only provided deterministic evidence. Do not change deterministic suggestions. "
        "Do not provide legal/compliance verdicts, and avoid terms GDPR/PII/compliant/non-compliant. "
        "Use cautious wording: may require review, deterministic evidence suggests, human reviewer should consider. "
        "Return strict JSON with keys llm_review_status, authority_note, field_reviews. "
        "Each field review must include column_name, review_note, ambiguity_note, suggested_reviewer_questions, evidence_limitations."
    )
    return [
        {"role": "system", "content": instruction},
        {"role": "user", "content": json.dumps(payload)},
    ]


def _clean_text(text: str) -> str:
    out = text
    for term in BANNED_TERMS:
        out = out.replace(term, "")
        out = out.replace(term.upper(), "")
        out = out.replace(term.title(), "")
    return out.strip()


def run_llm_review(payload: dict, model: str | None) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"llm_review_status": "skipped_missing_api_key", "authority_note": "LLM stage requested but skipped because OPENAI_API_KEY is not configured.", "field_reviews": []}

    try:
        from openai import OpenAI
    except Exception:
        return {"llm_review_status": "failed_fallback", "error_category": "openai_dependency_unavailable", "authority_note": "Deterministic artifacts remain authoritative evidence.", "field_reviews": []}

    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(model=model or DEFAULT_LLM_MODEL, input=_messages(payload))
        content = response.output_text
        parsed = json.loads(content)
    except Exception:
        return {"llm_review_status": "failed_fallback", "error_category": "llm_call_failed", "authority_note": "Deterministic artifacts remain authoritative evidence.", "field_reviews": []}

    parsed["llm_review_status"] = "completed"
    return parsed


def write_llm_artifacts(output_dir: Path, payload: dict, llm_result: dict) -> dict:
    safe_path = output_dir / "llm_safe_field_summary.json"
    json_path = output_dir / "llm_field_review.json"
    md_path = output_dir / "llm_field_review.md"

    safe_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    json_path.write_text(json.dumps(llm_result, indent=2), encoding="utf-8")

    lines = [
        "# LLM Field Review Notes",
        "",
        "This is an active LLM review over safe deterministic evidence.",
        "Deterministic outputs remain authoritative evidence.",
        "Human reviewer makes final decisions.",
        "",
        "## Authority boundary",
        f"- {llm_result.get('authority_note') or 'This review is advisory and non-authoritative.'}",
        "",
        f"## Status: {llm_result.get('llm_review_status')}",
    ]
    for item in llm_result.get("field_reviews", []):
        lines.extend([
            "",
            f"### `{item.get('column_name')}`",
            f"- Review note: {_clean_text(str(item.get('review_note', '')))}",
            f"- Ambiguity note: {_clean_text(str(item.get('ambiguity_note', '')))}",
            "- Suggested reviewer questions:",
        ])
        for q in item.get("suggested_reviewer_questions", []):
            lines.append(f"  - {_clean_text(str(q))}")
        lines.append("- Evidence limitations:")
        for lim in item.get("evidence_limitations", []):
            lines.append(f"  - {_clean_text(str(lim))}")

    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")

    return {
        "safe_field_summary_path": str(safe_path),
        "field_review_json_path": str(json_path),
        "field_review_markdown_path": str(md_path),
    }
