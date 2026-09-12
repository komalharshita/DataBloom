# AI Data Storyteller

Turn raw data into a story people can understand.

## Architecture

* **Frontend**: Next.js, React, Tailwind CSS, Plotly
* **Backend**: FastAPI, Pandas, OpenAI API
* **AI Service**: GPT-4o-mini generating structured insights and visualization definitions.

## How to run locally

1. **Frontend**:
    ```bash
    cd frontend
    npm run dev
    ```

2. **Backend**:
    ```bash
    cd backend
    # Activate virtual environment
    .\venv\Scripts\activate
    # Run API
    uvicorn main:app --reload
    ```

## Environment Variables
Create a `backend/.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
ALLOWED_ORIGINS=http://localhost:3000
```
