from agents.schema import AnalysisResult, VisualizationSpec, Metric, DataQualityIssue
from pydantic import ValidationError
import pytest

def test_analysis_result_valid():
    result = AnalysisResult(
        executive_summary="Test summary",
        key_metrics=[Metric(name="Total", value="100")],
        visualizations=[
            VisualizationSpec(title="Chart", type="bar", x="col_a", y="col_b", insight="Shows comparison")
        ],
        insights=["Insight 1"],
        recommendations=["Recommendation 1"],
        data_quality=[DataQualityIssue(issue="Missing values", severity="low")]
    )
    assert result.executive_summary == "Test summary"
    assert len(result.visualizations) == 1

def test_analysis_result_missing_required_field():
    with pytest.raises(ValidationError):
        AnalysisResult(
            key_metrics=[],
            visualizations=[],
            insights=[],
            recommendations=[],
            data_quality=[]
        )

def test_visualization_spec_missing_x():
    with pytest.raises(ValidationError):
        VisualizationSpec(
            title="Bad chart",
            type="bar",
            insight="No x column"
        )
