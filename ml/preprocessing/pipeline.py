from pathlib import Path
import json
import shutil
from typing import Any

from ml.preprocessing.audit import SUPPORTED_CHARTS, audit_records, write_outputs


REQUIRED_KEYS = {"executive_insight", "visualization_type", "visualization_spec"}


def preprocess_training_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only records that look usable for later visualization training.

    Does not assume every record is correct. Malformed examples are dropped
    and listed in the sidecar report by the caller.
    """
    kept = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        if "enhanced_prompt" in record and "enhanced_completion" in record:
            continue
        if not REQUIRED_KEYS.issubset(record.keys()) and not {
            "executive_insight",
            "visualization",
        }.issubset(record.keys()):
            continue
        spec = record.get("visualization_spec") or record.get("visualization") or {}
        if isinstance(spec, str):
            try:
                spec = json.loads(spec)
            except json.JSONDecodeError:
                continue
        if not isinstance(spec, dict):
            continue
        chart_type = (record.get("visualization_type") or spec.get("type") or spec.get("chart_type") or "").lower()
        if chart_type not in SUPPORTED_CHARTS | {"heatmap", "box"}:
            continue
        kept.append({
            "id": record.get("id", index),
            "visualization_type": chart_type,
            "visualization_spec": spec,
            "executive_insight": record.get("executive_insight") or record.get("insight"),
            "source_index": index,
        })
    return kept


def ingest_original(source: Path, raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    destination = raw_dir / "new dataset.json"
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)
    return destination


def run(raw_path: Path, processed_dir: Path) -> dict[str, Any]:
    raw_path = Path(raw_path)
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    if not raw_path.exists():
        report = {
            "status": "waiting_for_dataset",
            "message": "Place new dataset.json in data/raw/ without modifying the original file.",
            "kept": 0,
            "dropped": 0,
        }
        (processed_dir / "preprocessing_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report

    payload = json.loads(raw_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        records = payload.get("data") or payload.get("records") or payload.get("examples") or [payload]
    else:
        records = payload
    if not isinstance(records, list):
        records = []

    audit = audit_records(records)
    report = write_outputs(audit, processed_dir)
    report["status"] = "ok"
    report["source"] = str(raw_path)
    report["kept"] = audit["n_cleaned"]
    report["dropped"] = audit["n_records"] - audit["n_cleaned"]
    (processed_dir / "preprocessing_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    downloads = Path.home() / "Downloads" / "new dataset.json"
    raw_dir = root / "data" / "raw"
    if downloads.exists():
        ingest_original(downloads, raw_dir)
    candidates = [
        raw_dir / "new dataset.json",
        raw_dir / "new_dataset.json",
        downloads,
    ]
    raw = next((path for path in candidates if path.exists()), candidates[0])
    print(json.dumps(run(raw, root / "data" / "processed"), indent=2))
