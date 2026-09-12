import io
import json
from typing import Optional

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".json", ".xls", ".xlsx"}


def _extension(filename: Optional[str]) -> str:
    name = (filename or "").lower()
    for ext in (".xlsx", ".xls", ".json", ".csv"):
        if name.endswith(ext):
            return ext
    return ""


def parse_bytes(contents: bytes, filename: Optional[str]) -> pd.DataFrame:
    if not contents:
        raise ValueError("Uploaded file is empty.")

    ext = _extension(filename)
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file format. Upload CSV, JSON, or Excel.")

    buffer = io.BytesIO(contents)
    if ext == ".csv":
        df = pd.read_csv(buffer)
    elif ext == ".json":
        df = _parse_json(contents)
    else:
        df = pd.read_excel(buffer)

    if df is None or df.empty:
        raise ValueError("Uploaded dataset is empty.")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _parse_json(contents: bytes) -> pd.DataFrame:
    try:
        return pd.read_json(io.BytesIO(contents))
    except (ValueError, TypeError):
        payload = json.loads(contents.decode("utf-8"))
        if isinstance(payload, list):
            return pd.json_normalize(payload)
        if isinstance(payload, dict):
            for key in ("data", "records", "rows", "items"):
                if isinstance(payload.get(key), list):
                    return pd.json_normalize(payload[key])
            return pd.json_normalize([payload])
        raise ValueError("JSON file does not contain a table of records.")
