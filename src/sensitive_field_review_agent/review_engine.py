from __future__ import annotations

from dataclasses import asdict

from sensitive_field_review_agent.models import (
    DatasetProfile,
    DatasetReviewResult,
    DatasetSignals,
    FieldReviewEvidence,
    FieldReviewResult,
    FieldSignal,
    SensitiveFieldPolicy,
)

_DECISION_AUTHORITY_NOTE = (
    "This deterministic output supports triage only. A human reviewer decides final handling."
)


def _profile_summary(profile: DatasetProfile) -> dict[str, dict]:
    return {
        field.column_name: {
            "inferred_physical_type": field.inferred_physical_type,
            "null_ratio": field.null_ratio,
            "distinct_ratio": field.distinct_ratio,
            "string_length": {
                "min": field.string_min_length,
                "max": field.string_max_length,
                "avg": field.string_avg_length,
            },
        }
        for field in profile.field_profiles
    }


def _score_category(signals: list[FieldSignal], category: str, category_order: list[str]) -> tuple[int, int, int]:
    supporting = [s for s in signals if s.policy_category == category]
    pattern_count = sum(1 for s in supporting if s.signal_type == "pattern_family")
    return (pattern_count, len(supporting), -category_order.index(category))


def _evidence_for_signals(selected_signals: list[FieldSignal], category: str) -> list[FieldReviewEvidence]:
    evidence: list[FieldReviewEvidence] = []
    ordered_signals = sorted(
        selected_signals,
        key=lambda signal: 0 if signal.signal_type == "pattern_family" else 1,
    )
    for signal in ordered_signals:
        if signal.signal_type == "column_name_keyword":
            keyword = signal.evidence.matched_keyword or "<configured keyword>"
            summary = (
                f"Column name matched configured policy keyword '{keyword}' for category '{category}'."
            )
        else:
            summary = (
                "Configured pattern family "
                f"'{signal.signal_name}' met the policy threshold with "
                f"{signal.evidence.matched_count} of {signal.evidence.checked_count} checked values."
            )
        evidence.append(FieldReviewEvidence(signal_type=signal.signal_type, signal_name=signal.signal_name, summary=summary))
    return evidence


def generate_dataset_review(
    policy: SensitiveFieldPolicy,
    profile: DatasetProfile,
    signals: DatasetSignals,
) -> DatasetReviewResult:
    profile_by_name = _profile_summary(profile)
    category_order = list(policy.categories.keys())
    has_none_level = "none" in policy.review_levels

    results: list[FieldReviewResult] = []
    for field_signals in signals.fields:
        column_name = field_signals.column_name
        override = policy.field_overrides.get(column_name)
        profile_summary = profile_by_name.get(column_name, {})

        if override is not None:
            reviewer_questions = policy.categories[override.category].reviewer_questions
            review_required = override.review_level != "none"
            evidence = [
                FieldReviewEvidence(
                    signal_type="policy_override",
                    signal_name="field_override",
                    summary=(override.reason or "Policy field override configured for this column."),
                )
            ]
            results.append(
                FieldReviewResult(
                    column_name=column_name,
                    suggested_policy_category=override.category,
                    suggested_review_level=override.review_level,
                    confidence="policy_override",
                    review_required=review_required,
                    evidence_summary=evidence[0].summary,
                    supporting_signals=evidence,
                    profile_summary=profile_summary,
                    reviewer_questions=reviewer_questions,
                    decision_authority_note=_DECISION_AUTHORITY_NOTE,
                )
            )
            continue

        matched_signals = [s for s in field_signals.signals if s.matched]
        if not matched_signals:
            default_level = "none" if has_none_level else "low"
            results.append(
                FieldReviewResult(
                    column_name=column_name,
                    suggested_policy_category=None,
                    suggested_review_level=default_level,
                    confidence="none",
                    review_required=False,
                    evidence_summary="No configured deterministic field signals were observed.",
                    supporting_signals=[],
                    profile_summary=profile_summary,
                    reviewer_questions=[],
                    decision_authority_note=_DECISION_AUTHORITY_NOTE,
                )
            )
            continue

        best_category = sorted(
            {s.policy_category for s in matched_signals},
            key=lambda cat: _score_category(matched_signals, cat, category_order),
            reverse=True,
        )[0]
        selected_signals = [s for s in matched_signals if s.policy_category == best_category]
        confidence = "high" if any(s.signal_type == "pattern_family" for s in selected_signals) else "medium"
        evidence = _evidence_for_signals(selected_signals, best_category)

        results.append(
            FieldReviewResult(
                column_name=column_name,
                suggested_policy_category=best_category,
                suggested_review_level=policy.categories[best_category].default_review_level,
                confidence=confidence,
                review_required=True,
                evidence_summary=evidence[0].summary,
                supporting_signals=evidence,
                profile_summary=profile_summary,
                reviewer_questions=policy.categories[best_category].reviewer_questions,
                decision_authority_note=_DECISION_AUTHORITY_NOTE,
            )
        )

    return DatasetReviewResult(
        row_count=profile.row_count,
        column_count=profile.column_count,
        policy_name=policy.policy_name,
        policy_version=policy.policy_version,
        authority_note=policy.authority_note,
        fields=results,
    )


def dataset_review_to_dict(review: DatasetReviewResult) -> dict:
    return asdict(review)
