from typing import Any, Optional

import pandas as pd
import plotly.graph_objects as go

from agents.jsonutil import json_safe
from agents.profiler import detect_temporal_column
from agents.schema import VisualizationSpec

CHART_COLORS = ["#14b8a6", "#38bdf8", "#a78bfa", "#f59e0b", "#f43f5e", "#84cc16"]


class VisualizationAgent:
    def generate_chart_data(self, viz: VisualizationSpec, df: pd.DataFrame) -> dict[str, Any]:
        frame = df.copy()
        if viz.x in frame.columns and detect_temporal_column(frame, viz.x):
            frame[viz.x] = pd.to_datetime(frame[viz.x], errors="coerce")

        x_data: list[Any] = []
        y_data: list[Any] = []
        aggregation = "raw"

        try:
            if viz.type in ("bar", "pie"):
                x_data, y_data, aggregation = self._aggregate_category(frame, viz)
            elif viz.type == "line":
                x_data, y_data, aggregation = self._line_series(frame, viz)
            elif viz.type == "scatter":
                x_data, y_data, aggregation = self._scatter(frame, viz)
            elif viz.type == "histogram":
                sample = frame[viz.x].dropna()
                if len(sample) > 2000:
                    sample = sample.sample(2000, random_state=42)
                x_data = json_safe(sample.tolist())
                aggregation = "distribution"
            else:
                sample = frame.dropna(subset=[viz.x]).head(100)
                x_data = json_safe(sample[viz.x].tolist())
                if viz.y and viz.y in frame.columns:
                    y_data = json_safe(sample[viz.y].tolist())
        except Exception as exc:
            print(f"Error generating chart data for {viz.title}: {exc}")
            x_data, y_data = [], []

        x_data = json_safe(x_data)
        y_data = json_safe(y_data)
        figure = self._to_plotly_figure(viz, x_data, y_data)

        return {
            "title": viz.title,
            "type": viz.type,
            "x": viz.x,
            "y": viz.y,
            "insight": viz.insight,
            "rationale": viz.rationale,
            "aggregation": aggregation,
            "x_data": x_data,
            "y_data": y_data,
            "plotly": figure,
        }

    def _aggregate_category(self, frame: pd.DataFrame, viz: VisualizationSpec):
        if viz.y and viz.y in frame.columns and viz.y.lower() != "count":
            temp = frame.copy()
            temp["_y"] = pd.to_numeric(temp[viz.y], errors="coerce")
            agg = temp.groupby(viz.x, dropna=True)["_y"].sum().sort_values(ascending=False).head(20)
            return json_safe(agg.index.astype(str).tolist()), json_safe(agg.tolist()), f"sum({viz.y})"
        counts = frame[viz.x].dropna().astype(str).value_counts().head(20)
        return json_safe(counts.index.tolist()), json_safe(counts.tolist()), "count"

    def _line_series(self, frame: pd.DataFrame, viz: VisualizationSpec):
        if not viz.y or viz.y not in frame.columns:
            counts = frame[viz.x].value_counts().head(30)
            return json_safe(counts.index.astype(str).tolist()), json_safe(counts.tolist()), "count"
        temp = frame.dropna(subset=[viz.x, viz.y])
        if pd.api.types.is_datetime64_any_dtype(temp[viz.x]):
            temp = temp.sort_values(viz.x)
            grouped = temp.groupby(temp[viz.x].dt.to_period("M"), dropna=True)[viz.y].sum()
            x_vals = [str(idx) for idx in grouped.index]
            return json_safe(x_vals), json_safe(grouped.tolist()), f"monthly_sum({viz.y})"
        grouped = temp.groupby(viz.x, dropna=True)[viz.y].mean()
        return json_safe(grouped.index.astype(str).tolist()), json_safe(grouped.tolist()), f"mean({viz.y})"

    def _scatter(self, frame: pd.DataFrame, viz: VisualizationSpec):
        if not viz.y or viz.y not in frame.columns:
            return [], [], "unavailable"
        temp = frame.dropna(subset=[viz.x, viz.y])
        if len(temp) > 500:
            temp = temp.sample(500, random_state=42)
        return json_safe(temp[viz.x].tolist()), json_safe(temp[viz.y].tolist()), "sample"

    def _to_plotly_figure(self, viz: VisualizationSpec, x_data: list, y_data: list) -> dict:
        if viz.type == "pie":
            fig = go.Figure(data=[go.Pie(labels=x_data, values=y_data, hole=0.35, marker_colors=CHART_COLORS)])
        elif viz.type == "histogram":
            fig = go.Figure(data=[go.Histogram(x=x_data, marker_color=CHART_COLORS[0])])
        elif viz.type == "bar":
            fig = go.Figure(data=[go.Bar(x=x_data, y=y_data, marker_color=CHART_COLORS[0])])
        elif viz.type == "scatter":
            fig = go.Figure(data=[go.Scatter(x=x_data, y=y_data, mode="markers", marker=dict(color=CHART_COLORS[2], size=8))])
        else:
            fig = go.Figure(data=[go.Scatter(x=x_data, y=y_data, mode="lines+markers", line=dict(color=CHART_COLORS[0], width=3))])

        fig.update_layout(
            title=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.4)",
            font=dict(color="#e2e8f0", size=12),
            margin=dict(t=16, b=48, l=48, r=16),
            xaxis=dict(title=viz.x, gridcolor="rgba(148,163,184,0.2)", automargin=True),
            yaxis=dict(title=viz.y or "", gridcolor="rgba(148,163,184,0.2)", automargin=True),
            showlegend=False,
        )
        return json_safe(fig.to_plotly_json())
