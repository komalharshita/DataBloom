from typing import List

import pandas as pd

from agents.evidence import fallback_visualizations
from agents.schema import (
    SUPPORTED_CHART_TYPES,
    AnalysisResult,
    DataQualityIssue,
    VisualizationSpec,
)


class ValidatorAgent:
    def validate(self, result: AnalysisResult, df: pd.DataFrame, profile: dict) -> AnalysisResult:
        valid_visualizations: List[VisualizationSpec] = []
        warnings: List[str] = []
        columns = set(df.columns)

        for viz in result.visualizations:
            chart_type = (viz.type or "").lower()
            if chart_type not in SUPPORTED_CHART_TYPES:
                warnings.append(f"Rejected '{viz.title}': unsupported chart type '{viz.type}'.")
                continue
            if not viz.x or viz.x not in columns:
                warnings.append(f"Rejected '{viz.title}': column '{viz.x}' does not exist.")
                continue
            needs_y = chart_type in {"line", "scatter"}
            if needs_y and (not viz.y or (viz.y not in columns and viz.y.lower() != "count")):
                warnings.append(f"Rejected '{viz.title}': y column '{viz.y}' is required and missing.")
                continue
            if viz.y and viz.y.lower() != "count" and viz.y not in columns:
                warnings.append(f"Rejected '{viz.title}': column '{viz.y}' does not exist.")
                continue
            if not viz.title.strip() or not viz.insight.strip():
                warnings.append(f"Rejected a chart because title or insight was empty.")
                continue
            viz.type = chart_type
            valid_visualizations.append(viz)

        if not valid_visualizations:
            for item in fallback_visualizations(profile):
                if item["x"] in columns:
                    valid_visualizations.append(VisualizationSpec(**item))

        result.visualizations = valid_visualizations[:4]

        for warning in warnings:
            result.data_quality.append(DataQualityIssue(issue=warning, severity="medium"))

        result.insights = [i.strip() for i in result.insights if i and i.strip()][:8]
        result.recommendations = [i.strip() for i in result.recommendations if i and i.strip()][:6]
        return result
