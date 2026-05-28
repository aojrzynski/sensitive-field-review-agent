from __future__ import annotations

import re
from dataclasses import asdict

import pandas as pd

from sensitive_field_review_agent.models import (
    CategoryPolicy,
    DatasetSignals,
    FieldSignal,
    FieldSignalEvidence,
    FieldSignalSet,
    SensitiveFieldPolicy,
)


_EMAIL_RE = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
_PHONE_RE = re.compile(r"^(?:\+?44|0)\s*(?:\d\s*){9,10}$")
_UK_POSTCODE_RE = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$", re.IGNORECASE)
_DATE_RE = re.compile(r"^(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})$")
_NATIONAL_ID_RE = re.compile(r"^[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D]?$", re.IGNORECASE)
_ACCOUNT_NUMBER_RE = re.compile(r"^\d{8,12}$")
_CURRENCY_RE = re.compile(r"^(?:[£$€]\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+(?:\.\d{2})?)$")
_SECRET_RE = re.compile(r"(?:sk_(?:live|test)_[A-Za-z0-9]{8,}|token|secret|api[_-]?key)", re.IGNORECASE)


def _normalize_name(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    return re.sub(r"_+", "_", normalized)


def _tokenize_name(value: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", _normalize_name(value)) if token}


def _matches_family(value: str, family: str) -> bool:
    if family == "email_like":
        return bool(_EMAIL_RE.match(value))
    if family == "phone_like":
        return bool(_PHONE_RE.match(value))
    if family == "uk_postcode_like":
        return bool(_UK_POSTCODE_RE.match(value))
    if family == "date_like":
        return bool(_DATE_RE.match(value))
    if family == "national_id_like":
        return bool(_NATIONAL_ID_RE.match(value.replace(" ", "")))
    if family == "account_number_like":
        return bool(_ACCOUNT_NUMBER_RE.match(re.sub(r"\s+", "", value)))
    if family == "currency_or_amount_like":
        return bool(_CURRENCY_RE.match(value.replace(",", "")))
    if family == "secret_or_token_like":
        return bool(_SECRET_RE.search(value))
    return False


def _pattern_signal(column_name: str, category_name: str, family: str, series: pd.Series, min_count: int, min_ratio: float) -> FieldSignal | None:
    values = [str(v).strip() for v in series.dropna().tolist() if str(v).strip()]
    checked_count = len(values)
    if checked_count == 0:
        return None
    matched_count = sum(1 for value in values if _matches_family(value, family))
    matched_ratio = matched_count / checked_count
    threshold_met = matched_count >= min_count and matched_ratio >= min_ratio
    if not threshold_met:
        return None
    return FieldSignal(
        column_name=column_name,
        signal_type="pattern_family",
        signal_name=family,
        policy_category=category_name,
        evidence=FieldSignalEvidence(
            checked_count=checked_count,
            matched_count=matched_count,
            matched_ratio=matched_ratio,
            min_count=min_count,
            min_ratio=min_ratio,
            threshold_met=True,
        ),
        matched=True,
        notes=f"Values match the configured {family} pattern family at or above the policy threshold.",
    )


def _keyword_signal(column_name: str, category_name: str, category_policy: CategoryPolicy) -> list[FieldSignal]:
    normalized_column = _normalize_name(column_name)
    column_tokens = _tokenize_name(column_name)
    signals: list[FieldSignal] = []
    for keyword in category_policy.name_keywords:
        normalized_keyword = _normalize_name(keyword)
        keyword_tokens = _tokenize_name(keyword)
        if (
            normalized_column == normalized_keyword
            or normalized_keyword in normalized_column
            or bool(column_tokens & keyword_tokens)
        ):
            signals.append(
                FieldSignal(
                    column_name=column_name,
                    signal_type="column_name_keyword",
                    signal_name="policy_keyword_match",
                    policy_category=category_name,
                    evidence=FieldSignalEvidence(matched_keyword=keyword),
                    matched=True,
                    notes="Column name matched a configured policy keyword.",
                )
            )
            break
    return signals


def generate_dataset_signals(dataframe: pd.DataFrame, policy: SensitiveFieldPolicy) -> DatasetSignals:
    field_signal_sets: list[FieldSignalSet] = []
    for column_name in dataframe.columns.tolist():
        column_signals: list[FieldSignal] = []
        for category_name, category_policy in policy.categories.items():
            column_signals.extend(_keyword_signal(str(column_name), category_name, category_policy))
            for family in category_policy.pattern_families:
                signal = _pattern_signal(
                    column_name=str(column_name),
                    category_name=category_name,
                    family=family,
                    series=dataframe[column_name],
                    min_count=policy.thresholds.pattern_match_min_count,
                    min_ratio=policy.thresholds.pattern_match_min_ratio,
                )
                if signal is not None:
                    column_signals.append(signal)

        field_signal_sets.append(FieldSignalSet(column_name=str(column_name), signals=column_signals))

    return DatasetSignals(
        row_count=int(dataframe.shape[0]),
        column_count=int(dataframe.shape[1]),
        fields=field_signal_sets,
    )


def dataset_signals_to_dict(signals: DatasetSignals) -> dict:
    return asdict(signals)
