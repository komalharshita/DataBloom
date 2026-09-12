import pandas as pd
from agents.visualization import VisualizationAgent
from agents.schema import VisualizationSpec

def test_visualization_agent_bar_chart():
    df = pd.DataFrame({"Category": ["A", "B", "A", "C"], "Value": [10, 20, 30, 40]})
    spec = VisualizationSpec(title="Test", type="bar", x="Category", y="Value", insight="Test insight")
    agent = VisualizationAgent()
    chart_data = agent.generate_chart_data(spec, df)
    assert chart_data["title"] == "Test"
    assert chart_data["type"] == "bar"
    assert "A" in chart_data["x_data"]

def test_visualization_agent_count_fallback():
    df = pd.DataFrame({"Category": ["A", "A", "B"]})
    spec = VisualizationSpec(title="Count Test", type="bar", x="Category", y=None, insight="Test")
    agent = VisualizationAgent()
    chart_data = agent.generate_chart_data(spec, df)
    assert "A" in chart_data["x_data"]
    assert "B" in chart_data["x_data"]
    assert 2 in chart_data["y_data"]
    assert 1 in chart_data["y_data"]
