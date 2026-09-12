from typing import Any, Optional

import pandas as pd

from agents.analyst import AnalystAgent
from agents.profiler import run_profiler
from agents.evidence import compute_evidence
from agents.schema import AnalysisResult
from agents.storyteller import StorytellerAgent
from agents.validator import ValidatorAgent
from agents.visualization import VisualizationAgent


async def run_pipeline(df: pd.DataFrame, question: Optional[str] = None) -> dict[str, Any]:
    profile = run_profiler(df)
    evidence = compute_evidence(df, profile, question)

    analyst = AnalystAgent()
    used_ai = analyst.provider.__class__.__name__ != "DeterministicProvider"
    try:
        raw_result = await analyst.analyze(profile, evidence, question)
    except Exception:
        from agents.provider import DeterministicProvider

        used_ai = False
        provider = DeterministicProvider()
        raw_result = await provider.generate_structured_output(
            "",
            "EVIDENCE_JSON_START"
            + __import__("json").dumps({"profile": profile, "evidence": evidence})
            + "EVIDENCE_JSON_END",
            AnalysisResult,
        )

    storyteller = StorytellerAgent()
    narrated = storyteller.tell(raw_result, evidence, question)

    validator = ValidatorAgent()
    validated = validator.validate(narrated, df, profile)

    viz_agent = VisualizationAgent()
    charts = []
    for spec in validated.visualizations:
        chart = viz_agent.generate_chart_data(spec, df)
        if chart["x_data"]:
            charts.append(chart)

    profile_quality = [
        {"issue": item["issue"], "severity": item["severity"]}
        for item in profile.get("data_quality_issues", [])
    ]
    ai_quality = [{"issue": item.issue, "severity": item.severity} for item in validated.data_quality]
    combined = profile_quality + ai_quality

    return {
        "summary": validated.executive_summary,
        "executive_summary": validated.executive_summary,
        "key_metrics": [{"name": m.name, "value": m.value} for m in validated.key_metrics],
        "visualizations": charts,
        "insights": validated.insights,
        "recommendations": validated.recommendations,
        "data_quality": combined,
        "overview": profile.get("overview", {}),
        "columns": profile.get("columns", []),
        "sample_rows": profile.get("head", []),
        "used_ai": used_ai,
    }
