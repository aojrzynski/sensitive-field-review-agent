import pandas as pd
import pytest

from sensitive_field_review_agent.intake import load_dataset


def test_load_csv_success(tmp_path):
    path = tmp_path / "input.csv"
    path.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")

    dataframe, metadata = load_dataset(path)

    assert list(dataframe.columns) == ["a", "b"]
    assert metadata.row_count == 2
    assert metadata.column_count == 2
    assert metadata.sheet_name is None


def test_load_xlsx_default_sheet(tmp_path):
    path = tmp_path / "book.xlsx"
    pd.DataFrame({"a": [1]}).to_excel(path, sheet_name="First", index=False)

    _, metadata = load_dataset(path)
    assert metadata.sheet_name == "First"


def test_load_xlsx_explicit_sheet(tmp_path):
    path = tmp_path / "book.xlsx"
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame({"a": [1]}).to_excel(writer, sheet_name="First", index=False)
        pd.DataFrame({"a": [2]}).to_excel(writer, sheet_name="Second", index=False)

    dataframe, metadata = load_dataset(path, sheet="Second")
    assert metadata.sheet_name == "Second"
    assert dataframe.iloc[0, 0] == 2


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_dataset("does_not_exist.csv")


def test_unsupported_extension_raises(tmp_path):
    path = tmp_path / "input.txt"
    path.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported dataset extension"):
        load_dataset(path)


def test_missing_excel_sheet_raises(tmp_path):
    path = tmp_path / "book.xlsx"
    pd.DataFrame({"a": [1]}).to_excel(path, sheet_name="First", index=False)
    with pytest.raises(ValueError, match="Sheet 'Missing' not found"):
        load_dataset(path, sheet="Missing")


def test_zero_row_csv_raises(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("a,b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="zero rows"):
        load_dataset(path)
