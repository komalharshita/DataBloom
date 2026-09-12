import pandas as pd
from agents.validator import ValidatorAgent
from agents.profiler import run_profiler
from agents.schema import AnalysisResult, VisualizationSpec, Metric

def test_validator_removes_invalid_visualizations():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    profile = run_profiler(df)
    result = AnalysisResult(
        executive_summary="Summary",
        key_metrics=[Metric(name="Total", value="10")],
        visualizations=[
            VisualizationSpec(title="Valid", type="bar", x="A", y="B", insight="Insight 1"),
            VisualizationSpec(title="Invalid", type="line", x="MissingCol", y="B", insight="Insight 2")
        ],
        insights=[],
        recommendations=[],
        data_quality=[]
    )
    validator = ValidatorAgent()
    validated = validator.validate(result, df, profile)
    assert any(v.title == "Valid" for v in validated.visualizations)
    assert all(v.title != "Invalid" for v in validated.visualizations)
    assert any("MissingCol" in dq.issue for dq in validated.data_quality)
