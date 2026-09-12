import json
from functools import lru_cache
from pathlib import Path
from typing import Any

FEWSHOT_CANDIDATES = [
    Path(__file__).resolve().parents[2] / "data" / "processed" / "fewshot_examples.json",
    Path(__file__).resolve().parents[1] / "data" / "processed" / "fewshot_examples.json",
]


@lru_cache(maxsize=1)
def load_fewshot_examples(limit: int = 8) -> list[dict[str, Any]]:
    for path in FEWSHOT_CANDIDATES:
        try:
            if not path.exists():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                return payload[:limit]
        except (OSError, json.JSONDecodeError):
            return []
    return []


def fewshot_prompt_block(limit: int = 8) -> str:
    examples = load_fewshot_examples(limit)
    if not examples:
        return ""
    compact = []
    for example in examples:
        compact.append({
            "chart_type": example.get("chart_type"),
            "why_this_chart": example.get("why_this_chart"),
            "visualization": example.get("visualization"),
            "insight_style": example.get("insight_style"),
        })
    return (
        "\n\nVALIDATED FEW-SHOT STYLE EXAMPLES (from a curated external dataset).\n"
        "Use them only for chart-intent and writing style.\n"
        "Do NOT copy their numbers, columns, industries, or claims into this analysis.\n"
        + json.dumps(compact, ensure_ascii=True)
    )
