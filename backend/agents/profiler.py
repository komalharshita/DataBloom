from typing import Any

import numpy as np
import pandas as pd

from agents.jsonutil import json_safe


def detect_temporal_column(df: pd.DataFrame, col: str) -> bool:
    try:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return True
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            sample = df[col].dropna().head(20)
            if sample.empty:
                return False
            parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
            return bool(parsed.notna().mean() >= 0.8)
    except Exception:
        return False
    return False


def detect_outliers(series: pd.Series) -> int:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return 0
    q1 = numeric.quantile(0.25)
    q3 = numeric.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return int(((numeric < lower) | (numeric > upper)).sum())


def _is_categorical(series: pd.Series, unique_count: int, n_rows: int) -> bool:
    if pd.api.types.is_bool_dtype(series):
        return True
    if pd.api.types.is_numeric_dtype(series):
        return unique_count <= min(20, max(2, int(n_rows * 0.05)))
    return unique_count <= max(30, int(n_rows * 0.3))


def run_profiler(df: pd.DataFrame) -> dict[str, Any]:
    n_rows = int(len(df))
    n_cols = int(len(df.columns))
    n_duplicates = int(df.duplicated().sum())

    columns_info = []
    data_quality_issues = []
    numeric_columns = []
    categorical_columns = []
    datetime_columns = []

    if n_rows == 0:
        raise ValueError("Dataset has no rows.")

    if n_duplicates > 0:
        data_quality_issues.append({
            "issue": f"Found {n_duplicates} duplicate rows.",
            "severity": "medium",
        })

    for col in df.columns:
        series = df[col]
        n_missing = int(series.isnull().sum())
        missing_pct = n_missing / n_rows
        unique_values = int(series.nunique(dropna=True))
        is_temporal = detect_temporal_column(df, col)

        info: dict[str, Any] = {
            "name": str(col),
            "type": str(series.dtype),
            "missing_values": n_missing,
            "missing_percentage": round(missing_pct * 100, 2),
            "unique_values": unique_values,
            "is_temporal": is_temporal,
            "is_numeric": bool(pd.api.types.is_numeric_dtype(series) and not is_temporal),
            "is_categorical": False,
            "outliers": 0,
        }

        if missing_pct > 0.1:
            data_quality_issues.append({
                "issue": f"Column '{col}' has {round(missing_pct * 100, 1)}% missing values.",
                "severity": "high" if missing_pct > 0.5 else "medium",
            })

        if is_temporal:
            datetime_columns.append(str(col))
            parsed = pd.to_datetime(series, errors="coerce")
            valid = parsed.dropna()
            if not valid.empty:
                info["min"] = json_safe(valid.min())
                info["max"] = json_safe(valid.max())
        elif pd.api.types.is_numeric_dtype(series):
            numeric_columns.append(str(col))
            numeric = pd.to_numeric(series, errors="coerce")
            info["min"] = json_safe(numeric.min())
            info["max"] = json_safe(numeric.max())
            info["mean"] = json_safe(numeric.mean())
            info["median"] = json_safe(numeric.median())
            info["std"] = json_safe(numeric.std())
            n_outliers = detect_outliers(numeric)
            info["outliers"] = n_outliers
            if n_outliers > 0:
                data_quality_issues.append({
                    "issue": f"Column '{col}' contains {n_outliers} potential outliers (IQR method).",
                    "severity": "low",
                })
        else:
            info["is_categorical"] = _is_categorical(series, unique_values, n_rows)
            if info["is_categorical"]:
                categorical_columns.append(str(col))
                info["sample_values"] = [str(x) for x in series.dropna().astype(str).unique()[:8]]

        if info["is_categorical"] is False and not info["is_numeric"] and not is_temporal:
            if unique_values <= 30:
                info["is_categorical"] = True
                categorical_columns.append(str(col))
                info["sample_values"] = [str(x) for x in series.dropna().astype(str).unique()[:8]]

        columns_info.append(info)

    overview = {
        "rows": n_rows,
        "columns": n_cols,
        "duplicates": n_duplicates,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "datetime_columns": datetime_columns,
        "missing_cells": int(df.isna().sum().sum()),
    }

    return json_safe({
        "num_rows": n_rows,
        "num_columns": n_cols,
        "num_duplicates": n_duplicates,
        "overview": overview,
        "columns": columns_info,
        "data_quality_issues": data_quality_issues,
        "head": df.head(5).replace({np.nan: None}).to_dict(orient="records"),
    })
