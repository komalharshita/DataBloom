from typing import Any, Optional

import pandas as pd

from agents.jsonutil import json_safe
from agents.profiler import detect_temporal_column


def _is_rate_like(name: str) -> bool:
    lowered = name.lower()
    return any(token in lowered for token in ("rate", "rating", "percent", "pct", "ratio", "score"))


def _prepare_frame(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    for col in prepared.columns:
        if detect_temporal_column(prepared, col) and not pd.api.types.is_datetime64_any_dtype(prepared[col]):
            prepared[col] = pd.to_datetime(prepared[col], errors="coerce")
    return prepared


def compute_evidence(df: pd.DataFrame, profile: dict[str, Any], question: Optional[str] = None) -> dict[str, Any]:
    """Calculated facts the model may cite. Never invented."""
    frame = _prepare_frame(df)
    numeric_cols = sorted(
        [c["name"] for c in profile["columns"] if c.get("is_numeric")],
        key=lambda name: (_is_rate_like(name), name.lower() not in {"revenue", "sales", "amount", "units_sold", "profit"}),
    )
    categorical_cols = [c["name"] for c in profile["columns"] if c.get("is_categorical")]
    datetime_cols = [c["name"] for c in profile["columns"] if c.get("is_temporal")]

    numeric_summaries = {}
    for col in numeric_cols:
        series = pd.to_numeric(frame[col], errors="coerce")
        numeric_summaries[col] = {
            "count": int(series.notna().sum()),
            "sum": json_safe(series.sum()),
            "mean": json_safe(series.mean()),
            "median": json_safe(series.median()),
            "min": json_safe(series.min()),
            "max": json_safe(series.max()),
            "std": json_safe(series.std()),
        }

    category_breakdowns = {}
    for col in categorical_cols[:6]:
        counts = frame[col].dropna().astype(str).value_counts().head(12)
        category_breakdowns[col] = [{"value": str(k), "count": int(v)} for k, v in counts.items()]

    group_comparisons = []
    for cat in categorical_cols[:4]:
        for num in numeric_cols[:3]:
            metric_series = pd.to_numeric(frame[num], errors="coerce")
            use_mean = _is_rate_like(num)
            grouped = (
                metric_series.groupby(frame[cat]).mean()
                if use_mean
                else metric_series.groupby(frame[cat]).sum()
            )
            grouped = grouped.sort_values(ascending=False).head(8)
            if grouped.empty:
                continue
            rows = [{"group": str(idx), "value": json_safe(val)} for idx, val in grouped.items()]
            top = rows[0]
            group_comparisons.append({
                "by": cat,
                "metric": num,
                "aggregation": "mean" if use_mean else "sum",
                "top_group": top["group"],
                "top_value": top["value"],
                "values": rows,
            })

    time_trends = []
    for date_col in datetime_cols[:2]:
        dated = frame.dropna(subset=[date_col]).sort_values(date_col)
        if dated.empty:
            continue
        for num in numeric_cols[:2]:
            series = dated.set_index(date_col)[num]
            if not pd.api.types.is_numeric_dtype(series):
                continue
            monthly = series.resample("ME").sum()
            if monthly.empty:
                continue
            points = [{"period": idx.strftime("%Y-%m"), "value": json_safe(val)} for idx, val in monthly.items()]
            first = monthly.dropna()
            change = None
            if len(first) >= 2 and first.iloc[0]:
                change = json_safe((first.iloc[-1] - first.iloc[0]) / abs(first.iloc[0]) * 100)
            time_trends.append({
                "date_column": date_col,
                "metric": num,
                "grain": "month",
                "first_period": points[0]["period"] if points else None,
                "last_period": points[-1]["period"] if points else None,
                "pct_change_first_to_last": change,
                "points": points,
            })

    correlations = []
    if len(numeric_cols) >= 2:
        corr = frame[numeric_cols].corr(numeric_only=True)
        seen = set()
        for a in numeric_cols:
            for b in numeric_cols:
                if a >= b or (a, b) in seen:
                    continue
                seen.add((a, b))
                value = corr.loc[a, b] if a in corr.index and b in corr.columns else None
                if value is None or pd.isna(value):
                    continue
                abs_val = abs(float(value))
                if abs_val < 0.35:
                    continue
                correlations.append({
                    "column_a": a,
                    "column_b": b,
                    "pearson_r": json_safe(value),
                    "note": "This is an association, not evidence of causation.",
                })

    key_metrics = build_key_metrics(profile, numeric_summaries, group_comparisons, time_trends)

    return json_safe({
        "question": question or "Perform exploratory analysis.",
        "row_count": profile["num_rows"],
        "column_count": profile["num_columns"],
        "numeric_summaries": numeric_summaries,
        "category_breakdowns": category_breakdowns,
        "group_comparisons": group_comparisons,
        "time_trends": time_trends,
        "correlations": correlations,
        "key_metrics": key_metrics,
        "grounding_rules": [
            "Cite only numbers from this evidence pack.",
            "Do not invent columns, values, or business facts.",
            "Describe correlations as associations, never as causation.",
        ],
    })


def build_key_metrics(
    profile: dict[str, Any],
    numeric_summaries: dict[str, Any],
    group_comparisons: list[dict[str, Any]],
    time_trends: list[dict[str, Any]],
) -> list[dict[str, str]]:
    metrics = [
        {"name": "Rows", "value": f"{profile['num_rows']:,}"},
        {"name": "Columns", "value": f"{profile['num_columns']:,}"},
    ]

    preferred = ["Revenue", "Sales", "Amount", "Total", "Units_Sold", "Profit"]
    added = set()
    for name in preferred:
        if name in numeric_summaries:
            summary = numeric_summaries[name]
            label = "Total " + name.replace("_", " ")
            metrics.append({"name": label, "value": _format_number(summary.get("sum"))})
            added.add(name)
            if len(added) >= 2:
                break

    if not added:
        for name, summary in list(numeric_summaries.items())[:2]:
            metrics.append({
                "name": f"Total {name}",
                "value": _format_number(summary.get("sum")),
            })

    if group_comparisons:
        top = group_comparisons[0]
        metrics.append({
            "name": f"Top {top['by']}",
            "value": f"{top['top_group']}",
        })

    if time_trends and time_trends[0].get("pct_change_first_to_last") is not None:
        change = time_trends[0]["pct_change_first_to_last"]
        direction = "up" if change >= 0 else "down"
        metrics.append({
            "name": f"{time_trends[0]['metric']} trend",
            "value": f"{direction} {abs(change):.1f}%",
        })

    return metrics[:6]


def _format_number(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(number) >= 1000:
        return f"{number:,.0f}"
    if abs(number) >= 10:
        return f"{number:,.1f}"
    return f"{number:,.2f}"


def fallback_visualizations(profile: dict[str, Any]) -> list[dict[str, Any]]:
    numeric = [c["name"] for c in profile["columns"] if c.get("is_numeric")]
    categorical = [c["name"] for c in profile["columns"] if c.get("is_categorical")]
    temporal = [c["name"] for c in profile["columns"] if c.get("is_temporal")]
    specs = []

    if temporal and numeric:
        specs.append({
            "title": f"{numeric[0]} over time",
            "type": "line",
            "x": temporal[0],
            "y": numeric[0],
            "insight": f"Trend of {numeric[0]} across {temporal[0]} using calculated monthly/row values.",
        })
    if categorical and numeric:
        specs.append({
            "title": f"{numeric[0]} by {categorical[0]}",
            "type": "bar",
            "x": categorical[0],
            "y": numeric[0],
            "insight": f"Comparison of total {numeric[0]} across {categorical[0]}.",
        })
    if len(categorical) > 1:
        specs.append({
            "title": f"Share of {categorical[0] if not numeric else categorical[-1]}",
            "type": "pie",
            "x": categorical[-1] if numeric else categorical[0],
            "y": numeric[0] if numeric else None,
            "insight": "Category mix based on recorded values.",
        })
    if numeric:
        specs.append({
            "title": f"Distribution of {numeric[0]}",
            "type": "histogram",
            "x": numeric[0],
            "y": None,
            "insight": f"Spread of {numeric[0]} in the uploaded file.",
        })
    if len(numeric) >= 2:
        specs.append({
            "title": f"{numeric[0]} vs {numeric[1]}",
            "type": "scatter",
            "x": numeric[0],
            "y": numeric[1],
            "insight": f"Association between {numeric[0]} and {numeric[1]} (not causation).",
        })
    return specs[:4]
