from typing import Optional

from agents.schema import AnalysisResult, Metric


class StorytellerAgent:
    """Shapes executive language. Does not invent numbers."""

    def tell(
        self,
        result: AnalysisResult,
        evidence: dict,
        question: Optional[str],
    ) -> AnalysisResult:
        computed = [Metric(name=m["name"], value=str(m["value"])) for m in evidence.get("key_metrics", [])]
        if computed:
            result.key_metrics = computed

        if not result.executive_summary.strip():
            result.executive_summary = self._fallback_summary(evidence, question)

        if question and question.strip() and question.lower() not in result.executive_summary.lower():
            result.executive_summary = (
                f"In response to “{question.strip()}”: {result.executive_summary}"
            )

        if not result.insights:
            result.insights = [
                f"The file contains {evidence.get('row_count', 0)} rows and {evidence.get('column_count', 0)} columns."
            ]

        if not result.recommendations:
            result.recommendations = [
                "Validate the leading and lagging groups against operational knowledge before acting.",
            ]

        return result

    def _fallback_summary(self, evidence: dict, question: Optional[str]) -> str:
        q = question.strip() if question else "what stands out in this data"
        rows = evidence.get("row_count", 0)
        lead = ""
        if evidence.get("group_comparisons"):
            top = evidence["group_comparisons"][0]
            lead = f" {top['top_group']} is the leading {top['by']} by {top['metric']}."
        return f"This story is based on {rows} calculated rows answering {q}.{lead}"
