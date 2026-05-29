from __future__ import annotations

from pathlib import Path

import pandas as pd

from sensitive_field_review_agent.models import DatasetMetadata


def load_dataset(path: str | Path, sheet: str | None = None) -> tuple[pd.DataFrame, DatasetMetadata]:
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    extension = dataset_path.suffix.lower()
    if extension == ".csv":
        dataframe = pd.read_csv(dataset_path)
        sheet_name = None
    elif extension in {".xlsx", ".xlsm"}:
        if sheet is None:
            workbook = pd.ExcelFile(dataset_path)
            sheet_name = str(workbook.sheet_names[0])
        else:
            workbook = pd.ExcelFile(dataset_path)
            if sheet not in workbook.sheet_names:
                raise ValueError(
                    f"Sheet '{sheet}' not found in workbook. Available sheets: {workbook.sheet_names}"
                )
            sheet_name = sheet
        dataframe = pd.read_excel(dataset_path, sheet_name=sheet_name)
    else:
        raise ValueError(f"Unsupported dataset extension: {extension}. Supported formats: .csv, .xlsx, .xlsm")

    if dataframe.shape[0] == 0:
        raise ValueError("Loaded dataset has zero rows")
    if dataframe.shape[1] == 0:
        raise ValueError("Loaded dataset has zero columns")

    metadata = DatasetMetadata(
        source_path=dataset_path,
        file_name=dataset_path.name,
        file_extension=extension,
        sheet_name=sheet_name,
        row_count=int(dataframe.shape[0]),
        column_count=int(dataframe.shape[1]),
        columns=[str(column) for column in dataframe.columns.tolist()],
    )

    return dataframe, metadata
