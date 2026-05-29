from __future__ import annotations

from dataclasses import asdict
import re

import pandas as pd
from pandas.api.types import is_bool_dtype, is_datetime64_any_dtype, is_numeric_dtype

from sensitive_field_review_agent.models import DatasetProfile, FieldProfile, SafeExampleShape


_SAFE_PUNCTUATION = set("-_.@:/+()#")
_DATE_LIKE_RE = re.compile(
    r"^(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})$"
)


def _infer_physical_type(series: pd.Series) -> str:
    if is_bool_dtype(series):
        return "boolean"
    if is_numeric_dtype(series):
        return "number"
    if is_datetime64_any_dtype(series):
        return "datetime"

    non_null = series.dropna()
    if non_null.empty:
        return "unknown"

    string_values = non_null.astype(str).str.strip()
    string_values = string_values[string_values != ""]
    if string_values.empty:
        return "unknown"

    date_like = string_values.map(lambda value: bool(_DATE_LIKE_RE.match(value)))
    if float(date_like.mean()) < 0.9:
        return "string"

    parsed = pd.to_datetime(string_values[date_like], errors="coerce", format="mixed")
    if parsed.notna().mean() >= 0.9:
        return "datetime"
    return "string"


def _shape_char(char: str) -> str:
    if char.isalpha():
        return "A"
    if char.isdigit():
        return "9"
    if char.isspace():
        return "_"
    if char in _SAFE_PUNCTUATION:
        return char
    return "*"


def _build_shape(value: str) -> SafeExampleShape:
    letters = sum(1 for c in value if c.isalpha())
    digits = sum(1 for c in value if c.isdigit())
    whitespace = sum(1 for c in value if c.isspace())
    punctuation_or_symbols = len(value) - letters - digits - whitespace
    generalized_shape = "".join(_shape_char(c) for c in value)

    return SafeExampleShape(
        length=len(value),
        letters_count=letters,
        digits_count=digits,
        whitespace_count=whitespace,
        punctuation_or_symbol_count=punctuation_or_symbols,
        generalized_shape=generalized_shape,
    )


def profile_dataset(dataframe: pd.DataFrame, max_examples_per_field: int) -> DatasetProfile:
    field_profiles: list[FieldProfile] = []
    row_count = int(dataframe.shape[0])

    for column_name in dataframe.columns.tolist():
        series = dataframe[column_name]
        non_null = series.dropna()
        non_null_count = int(non_null.shape[0])
        null_count = int(row_count - non_null_count)
        distinct_count = int(non_null.nunique(dropna=True))
        null_ratio = float(null_count / row_count) if row_count else 0.0
        distinct_ratio = float(distinct_count / non_null_count) if non_null_count else 0.0
        inferred_type = _infer_physical_type(series)

        string_min_length: int | None = None
        string_max_length: int | None = None
        string_avg_length: float | None = None
        safe_example_shapes: list[SafeExampleShape] = []

        if inferred_type == "string":
            as_strings = non_null.astype(str)
            lengths = as_strings.str.len()
            if not lengths.empty:
                string_min_length = int(lengths.min())
                string_max_length = int(lengths.max())
                string_avg_length = float(lengths.mean())

            unique_values = as_strings.drop_duplicates().head(max_examples_per_field)
            safe_example_shapes = [_build_shape(value) for value in unique_values.tolist()]

        field_profiles.append(
            FieldProfile(
                column_name=str(column_name),
                row_count=row_count,
                non_null_count=non_null_count,
                null_count=null_count,
                null_ratio=null_ratio,
                distinct_count=distinct_count,
                distinct_ratio=distinct_ratio,
                inferred_physical_type=inferred_type,
                string_min_length=string_min_length,
                string_max_length=string_max_length,
                string_avg_length=string_avg_length,
                safe_example_shapes=safe_example_shapes,
            )
        )

    return DatasetProfile(row_count=row_count, column_count=int(dataframe.shape[1]), field_profiles=field_profiles)


def dataset_profile_to_dict(profile: DatasetProfile) -> dict:
    return asdict(profile)
