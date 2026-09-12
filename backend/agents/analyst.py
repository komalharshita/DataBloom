import json
from typing import Optional

from agents.fewshot import fewshot_prompt_block
from agents.provider import get_ai_provider
from agents.schema import AnalysisResult

SYSTEM_PROMPT = """
You are the DataBloom analyst. Interpret CALCULATED evidence about a dataset.

CRITICAL GROUNDING RULES:
1. Never invent numbers, columns, trends, or business facts.
2. Use only values present in the evidence pack or profile.
3. If evidence shows correlation, say association — never causation.
4. Visualization x and y MUST be exact column names from the profile.
5. Supported chart types: bar, line, scatter, pie, histogram.
6. Choose charts by intent: time → line, category comparison → bar, mix → pie, distribution → histogram, relationship → scatter.
7. Keep the executive summary to 3-5 sentences for a non-technical leader.
8. Recommendations must follow from the evidence, not generic advice unrelated to the file.
"""


class AnalystAgent:
    def __init__(self) -> None:
        self.provider = get_ai_provider()

    async def analyze(self, profile: dict, evidence: dict, question: Optional[str]) -> AnalysisResult:
        payload = {
            "profile": {
                "num_rows": profile.get("num_rows"),
                "num_columns": profile.get("num_columns"),
                "columns": [
                    {
                        "name": c["name"],
                        "type": c.get("type"),
                        "is_numeric": c.get("is_numeric"),
                        "is_categorical": c.get("is_categorical"),
                        "is_temporal": c.get("is_temporal"),
                        "missing_percentage": c.get("missing_percentage"),
                    }
                    for c in profile.get("columns", [])
                ],
            },
            "evidence": evidence,
            "question": question or "Perform exploratory analysis.",
        }
        user_content = (
            "EVIDENCE_JSON_START"
            + json.dumps(payload, default=str)
            + "EVIDENCE_JSON_END\n"
            + "Write structured analysis that a VP can read in 30 seconds."
        )
        return await self.provider.generate_structured_output(
            SYSTEM_PROMPT + fewshot_prompt_block(),
            user_content,
            AnalysisResult,
        )
