"""Audit visualization instruction records. Never mutates the original file."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SUPPORTED_CHARTS = {"bar", "line", "scatter", "pie", "histogram"}

CHART_ALIASES = {
    "bar chart": "bar",
    "column": "bar",
    "column chart": "bar",
    "grouped bar": "bar",
    "stacked bar": "bar",
    "horizontal bar": "bar",
    "line chart": "line",
    "area": "line",
    "area chart": "line",
    "scatter plot": "scatter",
    "scatterplot": "scatter",
    "bubble": "scatter",
    "pie chart": "pie",
    "doughnut": "pie",
    "donut": "pie",
    "histogram": "histogram",
}

UNSUPPORTED_FAMILIES = {
    "heatmap",
    "heat map",
    "combo",
    "dual-axis",
    "dual axis",
    "radar",
    "gauge",
    "sankey",
    "treemap",
    "box",
    "boxplot",
    "box plot",
    "violin",
    "choropleth",
    "waterfall",
    "funnel",
    "sunburst",
    "candlestick",
    "gantt",
    "network",
}

PRESCRIPTIVE_RE = re.compile(
    r"\b(should|must|immediate(?:ly)?|always|never|guaranteed?|prove[sd]?|inspect(?:ed)?|recommend(?:ed|ing)?|required|prioritiz(?:e|ing))\b",
    re.I,
)
CAUSAL_RE = re.compile(
    r"\b(caused?|caus(es|ing)|because(?: of)?|results? in|leads? to|driven by|drives|due to|impacted by|statistically significant)\b",
    re.I,
)
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _section(text: str, heading: str) -> str:
    pattern = rf"###\s*{re.escape(heading)}\s*:?\s*(.*?)(?=\n###\s|\Z)"
    match = re.search(pattern, text, re.S | re.I)
    return match.group(1).strip() if match else ""


def _extract_json_blob(text: str) -> tuple[Any | None, str | None]:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    candidate = fenced.group(1) if fenced else None
    if candidate is None:
        start = text.find("{")
        if start < 0:
            return None, "no_json_object"
        depth = 0
        in_str = False
        escape = False
        end = None
        for i, ch in enumerate(text[start:], start):
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end is None:
            return None, "unbalanced_braces"
        candidate = text[start:end]
    try:
        return json.loads(candidate), None
    except json.JSONDecodeError as exc:
        return None, f"json_decode:{exc.msg}"


def _normalize_chart_type(raw: str) -> tuple[str, str]:
    text = (raw or "").lower()
    text = re.sub(r"[^a-z0-9 \-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    found: list[tuple[int, str, str]] = []
    for alias, mapped in CHART_ALIASES.items():
        pos = text.find(alias)
        if pos >= 0:
            found.append((pos, mapped, alias))
    for supported in SUPPORTED_CHARTS:
        match = re.search(rf"\b{supported}\b", text)
        if match:
            found.append((match.start(), supported, supported))
    for family in UNSUPPORTED_FAMILIES:
        pos = text.find(family)
        if pos >= 0:
            found.append((pos, "unsupported", family))
    if not found:
        first = text.split(" ")[0] if text else "unknown"
        return "unknown", first
    found.sort(key=lambda row: (row[0], 0 if row[1] in SUPPORTED_CHARTS else 1))
    return found[0][1], found[0][2]


def _numbers_from_text(text: str) -> set[float]:
    values = set()
    for token in NUMBER_RE.findall(text or ""):
        try:
            values.add(round(float(token), 4))
        except ValueError:
            continue
    return values


def _walk_data_numbers(obj: Any, acc: list[float], in_data: bool = False) -> None:
    skip_keys = {
        "options", "plugins", "legend", "tooltip", "scales", "config", "$schema",
        "backgroundcolor", "bordercolor", "color", "range", "scale", "font",
        "pointRadius", "pointradius", "width", "height", "padding",
    }
    data_keys = {"data", "values", "datasets", "x", "y", "r", "labels", "source"}
    if isinstance(obj, dict):
        for key, value in obj.items():
            lowered = str(key).lower()
            if lowered in skip_keys:
                continue
            child_in = in_data or lowered in data_keys
            _walk_data_numbers(value, acc, child_in)
    elif isinstance(obj, list):
        for value in obj:
            _walk_data_numbers(value, acc, in_data)
    elif in_data and isinstance(obj, (int, float)) and not isinstance(obj, bool):
        if math.isfinite(obj):
            acc.append(float(obj))


def _spec_looks_visual(spec: dict) -> bool:
    keys = {k.lower() for k in spec.keys()}
    if any(k in keys for k in ("type", "data", "datasets", "mark", "encoding", "layer", "traces")):
        return True
    dumped = json.dumps(spec).lower()
    return any(token in dumped for token in ("bar", "line", "scatter", "pie", "histogram", "point", "arc"))


def _databloom_spec(chart_type: str, spec: dict, insight: str, rationale: str) -> dict[str, Any] | None:
    if chart_type not in SUPPORTED_CHARTS:
        return None
    title = ""
    if isinstance(spec.get("options"), dict):
        title = (
            spec.get("options", {})
            .get("plugins", {})
            .get("title", {})
            .get("text")
            or ""
        )
    title = title or spec.get("title") or spec.get("description") or ""
    x = y = None
    encoding = spec.get("encoding") if isinstance(spec.get("encoding"), dict) else {}
    if encoding:
        x = (encoding.get("x") or {}).get("field") if isinstance(encoding.get("x"), dict) else None
        y = (encoding.get("y") or {}).get("field") if isinstance(encoding.get("y"), dict) else None
    if spec.get("layer") and isinstance(spec["layer"], list) and spec["layer"]:
        enc = spec["layer"][0].get("encoding") if isinstance(spec["layer"][0], dict) else {}
        if isinstance(enc, dict):
            x = x or (enc.get("x") or {}).get("field") if isinstance(enc.get("x"), dict) else x
            y = y or (enc.get("y") or {}).get("field") if isinstance(enc.get("y"), dict) else y
    labels = spec.get("data", {}).get("labels") if isinstance(spec.get("data"), dict) else None
    if isinstance(labels, list) and labels and x is None:
        x = "category"
        y = "value"
    if spec.get("type") == "scatter" or chart_type == "scatter":
        x = x or "x"
        y = y or "y"
    if chart_type == "histogram":
        x = x or "value"
        y = None
    if chart_type == "pie" and not x:
        x = "category"
    if not x:
        return None
    return {
        "title": str(title)[:120] or f"{chart_type.title()} chart",
        "type": chart_type,
        "x": str(x),
        "y": None if chart_type in {"pie", "histogram"} and not y else (str(y) if y else "value"),
        "insight": insight[:400],
        "rationale": rationale[:280],
    }


def classify_record(index: int, record: Any) -> dict[str, Any]:
    flags: list[str] = []
    if not isinstance(record, dict):
        return {
            "source_index": index,
            "status": "malformed",
            "flags": ["non_object_record"],
        }

    prompt = record.get("enhanced_prompt") or record.get("prompt") or ""
    completion = record.get("enhanced_completion") or record.get("completion") or ""
    if not prompt or not completion:
        flags.append("missing_prompt_or_completion")

    rationale = _section(completion, "Chart Type & Rationale") or completion[:400]
    spec_section = _section(completion, "Visualization Specification") or completion
    insight = _section(completion, "Executive Insight") or record.get("executive_insight") or ""

    spec, spec_error = _extract_json_blob(spec_section)
    if spec_error:
        flags.append("invalid_json_specification")
        flags.append(spec_error)
    if spec is not None and not isinstance(spec, dict):
        flags.append("spec_not_object")
        spec = None

    mapped, family = _normalize_chart_type(rationale or json.dumps(spec or {}))
    if mapped == "unsupported":
        flags.append("unsupported_chart_family")
    elif mapped == "unknown":
        flags.append("unknown_chart_type")

    if spec is None or (isinstance(spec, dict) and not _spec_looks_visual(spec)):
        flags.append("non_visual_example")

    if insight and CAUSAL_RE.search(insight):
        flags.append("unsupported_causal_claim")
    if insight and PRESCRIPTIVE_RE.search(insight):
        flags.append("prescriptive_claim")

    hallucinated = False
    if spec is not None and prompt:
        prompt_nums = _numbers_from_text(prompt)
        spec_nums: list[float] = []
        _walk_data_numbers(spec, spec_nums, in_data=False)
        notable = [n for n in spec_nums if abs(n) not in {0, 1} and abs(n) < 1e7]
        missing = []
        for number in notable:
            if not any(math.isclose(number, p, rel_tol=0.02, abs_tol=0.051) for p in prompt_nums):
                missing.append(number)
        if notable and len(missing) / max(len(set(round(n, 4) for n in notable)), 1) > 0.35:
            hallucinated = True
            flags.append("potentially_hallucinated_values")

    databloom = _databloom_spec(mapped, spec or {}, insight.strip(), rationale.split("\n", 1)[0][:280]) if spec else None
    if mapped in SUPPORTED_CHARTS and spec and not databloom:
        flags.append("could_not_map_to_databloom_spec")

    prompt_hash = hashlib.md5(re.sub(r"\s+", " ", prompt.lower()).encode("utf-8")).hexdigest()
    spec_hash = hashlib.md5(json.dumps(spec, sort_keys=True, default=str).encode("utf-8")).hexdigest() if spec else ""

    status = "valid_visualization_task"
    blocking = {
        "missing_prompt_or_completion",
        "invalid_json_specification",
        "spec_not_object",
        "non_visual_example",
        "unsupported_chart_family",
        "unknown_chart_type",
        "could_not_map_to_databloom_spec",
        "non_object_record",
    }
    if set(flags) & blocking:
        status = "rejected"
    elif "unsupported_causal_claim" in flags or "prescriptive_claim" in flags or hallucinated:
        status = "valid_with_warnings"

    return {
        "source_index": index,
        "status": status,
        "flags": flags,
        "chart_family": family,
        "mapped_chart_type": mapped,
        "insight": insight.strip(),
        "rationale": rationale.split("\n", 1)[0][:280],
        "prompt_excerpt": re.sub(r"\s+", " ", prompt)[:400],
        "prompt_hash": prompt_hash,
        "spec_hash": spec_hash,
        "databloom_spec": databloom,
        "has_vega": bool(isinstance(spec, dict) and "$schema" in spec),
        "has_chartjs": bool(isinstance(spec, dict) and ("data" in spec and ("type" in spec or "options" in spec))),
    }


def _fewshot_score(item: dict[str, Any]) -> tuple:
    flags = set(item.get("flags") or [])
    insight = item.get("insight") or ""
    sentences = max(insight.count("."), 1)
    return (
        0 if item["status"] == "valid_visualization_task" else 1,
        0 if not flags else 1,
        abs(sentences - 2),
        len(insight),
        item["source_index"],
    )


def _observational_insight(insight: str) -> str:
    extra = re.compile(
        r"\b(adopting|shifting|encouraging|selecting|choice for|will |could be|ensures?)\b",
        re.I,
    )
    parts = re.split(r"(?<=[.!?])\s+", (insight or "").strip())
    first = parts[0] if parts else ""
    if PRESCRIPTIVE_RE.search(first) or CAUSAL_RE.search(first) or extra.search(first):
        return ""
    return first.strip()


def _fewshot_ok(item: dict[str, Any]) -> bool:
    if item.get("status") not in {"valid_visualization_task", "valid_with_warnings"}:
        return False
    blocking = {
        "invalid_json_specification",
        "unsupported_chart_family",
        "unknown_chart_type",
        "non_visual_example",
        "could_not_map_to_databloom_spec",
        "potentially_hallucinated_values",
        "duplicate_prompt",
        "duplicate_spec",
    }
    if set(item.get("flags") or []) & blocking:
        return False
    spec = item.get("databloom_spec") or {}
    x_name = str(spec.get("x") or "")
    excerpt = item.get("prompt_excerpt") or ""
    if x_name.lower() in {"category", "value", "x"}:
        return False
    rationale = (item.get("rationale") or "").lower()
    chart = item["databloom_spec"]["type"]
    if chart not in rationale.split(".")[0]:
        return False
    if x_name and x_name.lower() not in excerpt.lower() and x_name.replace("_", " ").lower() not in excerpt.lower():
        return False
    insight = _observational_insight(item.get("insight") or "")
    if len(insight) < 40 or len(insight) > 420:
        return False
    excerpt_nums = _numbers_from_text(item.get("prompt_excerpt") or "")
    insight_nums = [n for n in _numbers_from_text(insight) if abs(n) not in {0, 1, 2, 3}]
    if insight_nums and excerpt_nums:
        if not all(any(math.isclose(n, p, rel_tol=0.05, abs_tol=0.1) for p in excerpt_nums) for n in insight_nums):
            return False
    return True


def select_fewshot(cleaned: list[dict[str, Any]], per_type: int = 2, limit: int = 8) -> list[dict[str, Any]]:
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in cleaned:
        if not _fewshot_ok(item):
            continue
        by_type[item["databloom_spec"]["type"]].append(item)
    selected = []
    for chart in ("bar", "line", "scatter", "pie", "histogram"):
        ranked = sorted(by_type.get(chart, []), key=_fewshot_score)
        selected.extend(ranked[:per_type])
    selected = selected[:limit]
    fewshot = []
    for item in selected:
        spec = item["databloom_spec"]
        fewshot.append({
            "source_index": item["source_index"],
            "chart_type": spec["type"],
            "why_this_chart": spec.get("rationale") or item.get("rationale"),
            "visualization": {
                "title": spec["title"],
                "type": spec["type"],
                "x": spec["x"],
                "y": spec.get("y"),
            },
            "insight_style": _observational_insight(item["insight"])[:420],
            "prompt_excerpt": item["prompt_excerpt"],
        })
    return fewshot


def audit_records(records: list[Any]) -> dict[str, Any]:
    classified = [classify_record(i, rec) for i, rec in enumerate(records)]
    prompt_groups: dict[str, list[int]] = defaultdict(list)
    spec_groups: dict[str, list[int]] = defaultdict(list)
    for item in classified:
        if item.get("prompt_hash"):
            prompt_groups[item["prompt_hash"]].append(item["source_index"])
        if item.get("spec_hash"):
            spec_groups[item["spec_hash"]].append(item["source_index"])

    duplicate_prompts = {k: v for k, v in prompt_groups.items() if len(v) > 1}
    duplicate_specs = {k: v for k, v in spec_groups.items() if len(v) > 1}
    duplicate_indexes = set()
    for group in duplicate_prompts.values():
        duplicate_indexes.update(group[1:])
        for idx in classified:
            if idx["source_index"] in group[1:]:
                idx.setdefault("flags", []).append("duplicate_prompt")
    for group in duplicate_specs.values():
        duplicate_indexes.update(group[1:])
        for idx in classified:
            if idx["source_index"] in group[1:]:
                if "duplicate_spec" not in idx.get("flags", []):
                    idx.setdefault("flags", []).append("duplicate_spec")

    status_counts = Counter(item["status"] for item in classified)
    flag_counts = Counter(flag for item in classified for flag in item.get("flags", []))
    chart_counts = Counter(item.get("mapped_chart_type") for item in classified)

    cleaned = []
    seen_prompts = set()
    for item in classified:
        if item["status"] not in {"valid_visualization_task", "valid_with_warnings"}:
            continue
        if item["prompt_hash"] in seen_prompts:
            continue
        if "duplicate_prompt" in item.get("flags", []):
            continue
        if not item.get("databloom_spec"):
            continue
        seen_prompts.add(item["prompt_hash"])
        cleaned.append({
            "source_index": item["source_index"],
            "status": item["status"],
            "flags": item["flags"],
            "mapped_chart_type": item["mapped_chart_type"],
            "insight": item["insight"],
            "rationale": item["rationale"],
            "databloom_spec": item["databloom_spec"],
            "prompt_excerpt": item["prompt_excerpt"],
        })

    fewshot = select_fewshot(cleaned)
    return {
        "n_records": len(records),
        "status_counts": dict(status_counts),
        "flag_counts": dict(flag_counts),
        "chart_type_counts": dict(chart_counts),
        "duplicate_prompt_groups": len(duplicate_prompts),
        "duplicate_spec_groups": len(duplicate_specs),
        "n_duplicate_records": len(duplicate_indexes),
        "n_cleaned": len(cleaned),
        "n_fewshot": len(fewshot),
        "classified": classified,
        "cleaned": cleaned,
        "fewshot": fewshot,
    }


def write_outputs(audit: dict[str, Any], processed_dir: Path) -> dict[str, Any]:
    processed_dir.mkdir(parents=True, exist_ok=True)
    (processed_dir / "cleaned_visualization_examples.json").write_text(
        json.dumps(audit["cleaned"], indent=2), encoding="utf-8"
    )
    (processed_dir / "fewshot_examples.json").write_text(
        json.dumps(audit["fewshot"], indent=2), encoding="utf-8"
    )
    report = {k: v for k, v in audit.items() if k not in {"classified", "cleaned", "fewshot"}}
    report["fewshot_source_indexes"] = [item["source_index"] for item in audit["fewshot"]]
    report["notes"] = [
        "Original file was not modified.",
        "Cleaned examples are derived and may omit Chart.js/Vega payloads.",
        "Few-shot examples are style guides only; they must not override calculated evidence.",
    ]
    (processed_dir / "audit_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    rejections = [
        {
            "source_index": item["source_index"],
            "status": item["status"],
            "flags": item["flags"],
            "chart_family": item.get("chart_family"),
        }
        for item in audit["classified"]
        if item["status"] == "rejected"
    ]
    (processed_dir / "rejected_examples.json").write_text(json.dumps(rejections, indent=2), encoding="utf-8")
    return report
