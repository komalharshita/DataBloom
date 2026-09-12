from typing import Any


def summarize_report(report: dict[str, Any]) -> str:
    if report.get("status") != "ok":
        return report.get("message", "Dataset not yet provided.")
    return f"Kept {report['kept']} usable examples and dropped {report['dropped']} malformed or unsuitable records."
