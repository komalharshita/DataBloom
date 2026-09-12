import pandas as pd
from pydantic import ValidationError
import pytest

from agents.evidence import compute_evidence
from agents.profiler import run_profiler
from agents.schema import AnalysisResult, VisualizationSpec
from agents.validator import ValidatorAgent
from agents.visualization import VisualizationAgent


def _sample_df():
    return pd.DataFrame({
        "Date": ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"],
        "Region": ["North", "South", "North", "East"],
        "Revenue": [100, 140, 180, 90],
        "Units": [10, 12, 15, 8],
    })


def test_profiler_missing_and_outliers():
    df = pd.DataFrame({
        "A": [1, 2, 3, 4, 100],
        "B": ["cat", "dog", "cat", None, "mouse"],
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
    })
    profile = run_profiler(df)
    assert profile["num_rows"] == 5
    date_col = next(c for c in profile["columns"] if c["name"] == "Date")
    assert date_col["is_temporal"] is True
    a_col = next(c for c in profile["columns"] if c["name"] == "A")
    assert a_col["outliers"] == 1
    b_col = next(c for c in profile["columns"] if c["name"] == "B")
    assert b_col["missing_values"] == 1


def test_empty_profiler_rejected():
    with pytest.raises(ValueError):
        run_profiler(pd.DataFrame({"A": []}))


def test_evidence_group_comparison():
    df = _sample_df()
    profile = run_profiler(df)
    evidence = compute_evidence(df, profile, "Which region is performing best?")
    assert evidence["group_comparisons"]
    north = next(
        item for item in evidence["group_comparisons"]
        if item["by"] == "Region" and item["metric"] == "Revenue"
    )
    assert north["top_group"] == "North"
    assert north["top_value"] == 280


def test_malformed_ai_response():
    with pytest.raises(ValidationError):
        AnalysisResult.model_validate({"insights": ["only insights"]})


def test_validator_invalid_column_and_chart_type():
    df = _sample_df()
    profile = run_profiler(df)
    result = AnalysisResult(
        executive_summary="Summary",
        visualizations=[
            VisualizationSpec(title="Valid", type="bar", x="Region", y="Revenue", insight="ok"),
            VisualizationSpec(title="Missing", type="line", x="Nope", y="Revenue", insight="bad"),
            VisualizationSpec(title="BadType", type="sankey", x="Region", y="Revenue", insight="bad"),
        ],
        insights=["ok"],
        recommendations=["ok"],
    )
    validated = ValidatorAgent().validate(result, df, profile)
    titles = [v.title for v in validated.visualizations]
    assert "Valid" in titles
    assert "Missing" not in titles
    assert any("Nope" in dq.issue for dq in validated.data_quality)
    assert any("unsupported" in dq.issue.lower() for dq in validated.data_quality)


def test_chart_generation_and_plotly_payload():
    df = _sample_df()
    spec = VisualizationSpec(title="Revenue by region", type="bar", x="Region", y="Revenue", insight="totals")
    chart = VisualizationAgent().generate_chart_data(spec, df)
    assert "North" in chart["x_data"]
    assert chart["plotly"]["data"]
    hist = VisualizationAgent().generate_chart_data(
        VisualizationSpec(title="Dist", type="histogram", x="Revenue", insight="spread"),
        df,
    )
    assert hist["x_data"]
