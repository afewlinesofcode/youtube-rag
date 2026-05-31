# YouTube RAG

A single-page FastAPI app that ingests a YouTube transcript, chunks it with LangChain, stores OpenAI embeddings in PostgreSQL with pgvector, and opens a chat scoped to that video.

## Setup

1. Start PostgreSQL:

```bash
docker compose up -d
```

2. Create and fill `.env`:

```bash
cp .env.example .env
```

3. Install backend dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Install frontend dependencies:

```bash
cd frontend
npm install
```

5. Run the backend API:

```bash
uvicorn app.main:app --reload
```

6. Run the frontend app in a second terminal:

```bash
cd frontend
npm run dev
```

Open the frontend at `http://localhost:5173`.

For a production frontend build, run `cd frontend && npm run build`. If the frontend is hosted on a different origin than FastAPI, set `VITE_API_BASE_URL` to the backend base URL.

## Docker Development

Run the full development stack (PostgreSQL, backend, and frontend) with one command:

```bash
docker compose up --build
```

This starts:

- Frontend (Vite dev server): `http://localhost:5173`
- Backend API: `http://localhost:8000`
- PostgreSQL with pgvector: internal compose service (`postgres:5432`)
- Redis queue broker: internal compose service (`redis:6379`)
- Celery worker for ingestion jobs

The compose setup bind-mounts your local source directories into containers, so editing code locally is reflected immediately:

- Frontend runs `npm run dev` with HMR.
- Backend runs `uvicorn app.main:app --reload`.
- Worker runs Celery to process long-running video ingestion jobs.

When running through Docker, compose overrides `DATABASE_URL` for the backend to use the `postgres` service hostname.

To stop the stack:

```bash
docker compose down
```

## Notes

- The backend first tries `YoutubeLoader` transcript tracks, then falls back to audio transcription for videos without text tracks.
- Transcription mode is controlled by `TRANSCRIPTION_MODE` (`openai` or `local`).
- If yt-dlp reports "Sign in to confirm you're not a bot", export YouTube cookies and set `YT_DLP_COOKIES_FILE`.
- In Docker, mount the cookies file into backend and worker containers and point `YT_DLP_COOKIES_FILE` to that in-container path.
- Read-only cookie mounts are supported: the app copies the cookie file to a writable temp location before calling yt-dlp.
- Cookie file can be Netscape cookies.txt, or a JSON cookie export (the app will convert JSON to Netscape format automatically).
- If you see "does not look like a Netscape format cookies file", verify `.cookies/youtube.txt` is not empty.

Example Docker setup:

1. Place exported cookies at `.cookies/youtube.txt`.
2. Set `YT_DLP_COOKIES_FILE=/app/.cookies/youtube.txt` in `.env`.
3. Restart services: `docker compose up -d --build`.

`docker-compose.yml` already mounts `./.cookies` into `/app/.cookies` for backend and worker.

- Video processing is asynchronous: `POST /api/videos/process` queues a job and `GET /api/videos/process/{job_id}` reports status.
- `videos` stores the generated title/topic and document id.
- `chat_messages` stores the conversation history for each processed video.
- `process_jobs` stores asynchronous ingestion job state.
- Transcript chunks and embeddings are stored by `langchain-postgres` in pgvector tables under the `youtube_transcripts` collection.
- The new frontend lives under `frontend/` and talks to the FastAPI API under `/api`.
