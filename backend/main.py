from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
import pandas as pd
import io
import os
import json

from services.data_profiler import profile_dataframe
from services.ai_service import analyze_data

app = FastAPI(title="AI Data Storyteller API", version="1.0.0")

# Configure CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisResponse(BaseModel):
    summary: str
    key_metrics: List[dict]
    visualizations: List[dict]
    insights: List[str]
    data_quality: List[dict]
    recommendations: List[str]

@app.get("/")
def read_root():
    return {"message": "AI Data Storyteller API is running"}

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_upload(
    file: UploadFile = File(...),
    question: Optional[str] = Form(None)
):
    # 1. Read the uploaded file
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith('.json'):
            df = pd.read_json(io.BytesIO(contents))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV, JSON, or Excel.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # 2. Profile the dataset
    try:
        profile_summary = profile_dataframe(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error profiling data: {str(e)}")

    # 3. Analyze with AI
    try:
        analysis_result = await analyze_data(df, profile_summary, question)
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing data: {str(e)}")

