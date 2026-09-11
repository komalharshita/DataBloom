import os
import json
import pandas as pd
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import List, Optional

class AIServiceProvider:
    async def analyze(self, df: pd.DataFrame, profile: dict, question: Optional[str]) -> dict:
        raise NotImplementedError

class OpenAIProvider(AIServiceProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def analyze(self, df: pd.DataFrame, profile: dict, question: Optional[str]) -> dict:
        if not self.client:
            raise Exception("OPENAI_API_KEY is not set.")

        system_prompt = \"\"\"
You are an expert AI Data Storyteller. Your job is to analyze dataset profiles and user questions to produce a plain-English executive summary, key metrics, recommended visualizations, insights, and data quality observations. 

CRITICAL RULE:
- NEVER invent information.
- All numerical claims must be traceable to the uploaded dataset.
- Recommend Plotly-compatible visualization specifications. For each visualization, provide the 'type' (e.g., 'bar', 'scatter', 'line', 'pie', 'histogram'), 'x' (column name), 'y' (column name), and a 'title'. If 'y' is an aggregation, specify it clearly, or just use the raw column if it's a scatter. The backend will map these columns to actual data points.

Provide output as a structured JSON object matching this schema exactly:
{
  "summary": "Plain English summary of findings",
  "key_metrics": [{"name": "Metric Name", "value": "Value"}],
  "visualizations": [
    {
      "title": "Chart Title",
      "type": "bar",
      "x": "exact_column_name_from_profile",
      "y": "exact_column_name_from_profile",
      "insight": "Short explanation of what this shows"
    }
  ],
  "insights": ["Insight 1", "Insight 2"],
  "data_quality": [{"issue": "Issue description", "severity": "low|medium|high"}],
  "recommendations": ["Recommendation 1"]
}
\"\"\"

        user_content = f"Dataset Profile:\n{json.dumps(profile, indent=2)}\n\n"
        if question:
            user_content += f"User Question: {question}\n\n"
        else:
            user_content += "Perform an exploratory analysis to find the most interesting trends or patterns.\n\n"

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2
        )

        try:
            result = json.loads(response.choices[0].message.content)
            
            # Combine generated data quality with profile data quality
            if "data_quality_issues" in profile:
                profile_dq = [{"issue": f"{dq['column']}: {dq['description']}", "severity": dq["severity"]} for dq in profile["data_quality_issues"]]
                result["data_quality"] = profile_dq + result.get("data_quality", [])
                
            # Populate data for visualizations
            for viz in result.get("visualizations", []):
                x_col = viz.get("x")
                y_col = viz.get("y")
                # Ensure the requested columns actually exist
                if x_col in df.columns and y_col in df.columns:
                    # For MVP, we'll just take top 100 rows to avoid giant payload
                    sample_df = df.dropna(subset=[x_col, y_col]).head(100)
                    viz["x_data"] = sample_df[x_col].tolist()
                    viz["y_data"] = sample_df[y_col].tolist()
                elif x_col in df.columns and (not y_col or y_col == "count"):
                    # If only x is provided (e.g. histogram or pie), do a value count
                    counts = df[x_col].value_counts().head(20)
                    viz["x_data"] = counts.index.tolist()
                    viz["y_data"] = counts.values.tolist()
                else:
                    # Fallback empty
                    viz["x_data"] = []
                    viz["y_data"] = []
            
            return result
        except Exception as e:
            raise Exception(f"Failed to parse AI response: {str(e)}")

def get_ai_provider() -> AIServiceProvider:
    return OpenAIProvider()

async def analyze_data(df: pd.DataFrame, profile: dict, question: Optional[str]) -> dict:
    provider = get_ai_provider()
    return await provider.analyze(df, profile, question)
