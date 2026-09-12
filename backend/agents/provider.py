import json
import os
from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class AIProvider:
    async def generate_structured_output(
        self,
        system_prompt: str,
        user_content: str,
        response_model: Type[T],
    ) -> T:
        raise NotImplementedError


class APIProvider(AIProvider):
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None
        if self.api_key:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(api_key=self.api_key)

    @property
    def available(self) -> bool:
        return self.client is not None

    async def generate_structured_output(
        self,
        system_prompt: str,
        user_content: str,
        response_model: Type[T],
    ) -> T:
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                response_format=response_model,
                temperature=0.2,
            )
            parsed = response.choices[0].message.parsed
            if parsed:
                return parsed
            content = response.choices[0].message.content or "{}"
            return response_model.model_validate_json(content)
        except Exception:
            response = await self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt + "\nReturn valid JSON only."},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content or "{}"
            return response_model.model_validate_json(content)


class DeterministicProvider(AIProvider):
    """Offline / no-key fallback that only uses calculated evidence."""

    async def generate_structured_output(
        self,
        system_prompt: str,
        user_content: str,
        response_model: Type[T],
    ) -> T:
        raw = user_content
        if "EVIDENCE_JSON_START" in user_content:
            raw = user_content.split("EVIDENCE_JSON_START", 1)[-1].split("EVIDENCE_JSON_END", 1)[0]
        payload = json.loads(raw)
        evidence = payload.get("evidence", payload)
        profile = payload.get("profile", {})
        question = evidence.get("question", "exploratory analysis")
        metrics = [ {"name": m["name"], "value": m["value"]} for m in evidence.get("key_metrics", []) ]
        insights = []
        for comparison in evidence.get("group_comparisons", [])[:3]:
            agg = comparison.get("aggregation", "sum")
            verb = "averaging" if agg == "mean" else "totaling"
            insights.append(
                f"{comparison['top_group']} leads {comparison['by']} with {comparison['metric']} {verb} {comparison['top_value']}."
            )
        for trend in evidence.get("time_trends", [])[:2]:
            change = trend.get("pct_change_first_to_last")
            if change is None:
                continue
            direction = "increased" if change >= 0 else "decreased"
            insights.append(
                f"{trend['metric']} {direction} {abs(change):.1f}% from {trend['first_period']} to {trend['last_period']}."
            )
        for corr in evidence.get("correlations", [])[:2]:
            insights.append(
                f"{corr['column_a']} and {corr['column_b']} are associated (r={corr['pearson_r']:.2f}). This is correlation, not causation."
            )
        if not insights:
            insights.append(
                f"The dataset has {evidence.get('row_count', 0)} rows and {evidence.get('column_count', 0)} columns. Review the calculated metrics and charts."
            )

        recommendations = [
            "Treat every number on this page as calculated from the uploaded file, not estimated.",
            "Investigate the leading category and the lowest-performing group before changing strategy.",
        ]
        if evidence.get("time_trends"):
            recommendations.append("Monitor the time trend and confirm it continues in newer data.")

        from agents.evidence import fallback_visualizations
        from agents.schema import VisualizationSpec

        viz_specs = fallback_visualizations(profile) if profile else []
        visualizations = [
            VisualizationSpec(
                title=item["title"],
                type=item["type"],
                x=item["x"],
                y=item.get("y"),
                insight=item["insight"],
                rationale="Selected from column types in the profile.",
            )
            for item in viz_specs
        ]

        summary = (
            f"Based on {evidence.get('row_count', 0)} calculated rows, "
            f"the strongest pattern in this file is described in the metrics and charts below. "
            f"Question addressed: {question}."
        )
        if insights:
            summary = insights[0] + " " + summary

        data = {
            "executive_summary": summary,
            "key_metrics": metrics,
            "visualizations": [v.model_dump() for v in visualizations],
            "insights": insights[:5],
            "recommendations": recommendations[:4],
            "data_quality": [],
        }
        return response_model.model_validate(data)


def get_ai_provider() -> AIProvider:
    provider_type = os.getenv("AI_PROVIDER_TYPE", "api").lower()
    if provider_type == "deterministic":
        return DeterministicProvider()
    api = APIProvider()
    if not api.available:
        return DeterministicProvider()
    return api
