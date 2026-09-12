from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

SUPPORTED_CHART_TYPES = ("bar", "line", "scatter", "pie", "histogram")
ChartType = Literal["bar", "line", "scatter", "pie", "histogram"]


class DataQualityIssue(BaseModel):
    issue: str
    severity: Literal["low", "medium", "high"] = "medium"


class Metric(BaseModel):
    name: str
    value: str


class VisualizationSpec(BaseModel):
    title: str
    type: str = Field(..., description="One of: bar, line, scatter, pie, histogram")
    x: str = Field(..., description="Exact column name for x-axis or labels")
    y: Optional[str] = Field(None, description="Exact column name for y-axis if required")
    insight: str = Field(..., description="Short explanation grounded in calculated evidence")
    rationale: Optional[str] = Field(None, description="Why this chart type was selected")

    @field_validator("type")
    @classmethod
    def normalize_type(cls, value: str) -> str:
        cleaned = value.strip().lower()
        aliases = {"column": "bar", "bar chart": "bar", "line chart": "line", "pie chart": "pie"}
        return aliases.get(cleaned, cleaned)


class AnalysisResult(BaseModel):
    executive_summary: str
    key_metrics: List[Metric] = Field(default_factory=list)
    visualizations: List[VisualizationSpec] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    data_quality: List[DataQualityIssue] = Field(default_factory=list)
