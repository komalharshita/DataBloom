# DataBloom

Turn raw data into a story people can understand.

DataBloom is an AI data storytelling app. Upload CSV, JSON, or Excel and get:

1. Dataset overview
2. Executive summary
3. Calculated key metrics
4. Interactive Plotly charts
5. Insights
6. Recommendations
7. Data quality notes

Numbers come from Pandas. The model interprets those numbers. It does not invent them.

## 90-second demo

1. Open the app and click **Try Demo**.
2. Show the overview, metrics, charts, insights, and recommendations.
3. Optionally upload your own file and ask: “Which region is performing best?”

## Local setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
copy .env.example .env       # then add OPENAI_API_KEY
uvicorn main:app --reload --port 8000
```

Without an API key the demo still runs using calculated Python evidence.

### Frontend

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment

See `.env.example`. Never commit `.env` files or API keys.

```
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
AI_PROVIDER_TYPE=api
ALLOWED_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

`AI_PROVIDER_TYPE=deterministic` forces the no-key fallback.

## Architecture

```
profiler     → Pandas profile (types, missing, outliers, dates)
evidence     → calculated metrics, group totals, trends, correlations
analyst      → AI interpretation of evidence
storyteller  → executive wording; metrics remain calculated
validator    → drop bad columns / chart types
visualization→ Plotly JSON from validated specs
```

The model never emits frontend JavaScript. Charts are built on the backend.

## Sample data

`data/sample/sales_data.csv` includes time, regions, products, revenue, units, ratings, and return rates.

## External visualization dataset

The original `new dataset.json` is copied to `data/raw/` and is never edited.

Audit findings: `docs/DATASET.md`. Few-shot style examples: `data/processed/fewshot_examples.json` (loaded by the analyst, never as facts about a user upload).

```bash
python ml/preprocessing/pipeline.py
```

## Tests

```bash
cd backend
pytest -q
cd ../frontend
npm run build
```

## Deploy

See `docs/DEPLOY.md`.
