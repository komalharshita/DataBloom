# Deployment

## Frontend (Vercel)

1. Set `NEXT_PUBLIC_API_URL` to the public backend URL.
2. Deploy the `frontend` directory.

## Backend (Render / Railway / Fly)

1. Use the repository `Dockerfile` or start `uvicorn main:app --host 0.0.0.0 --port $PORT` from `backend`.
2. Set `OPENAI_API_KEY`, `OPENAI_MODEL`, and `ALLOWED_ORIGINS` (your Vercel URL).

HEALTHCHECK: `GET /api/health`

The demo endpoint is `POST /api/demo`.
