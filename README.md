# YouTube RAG Chat

A production-shaped Python LLM/RAG application around a real user workflow.

The app accepts a YouTube URL, extracts or transcribes the video content, chunks the transcript, stores OpenAI embeddings in PostgreSQL with pgvector, and opens a chat scoped to that video. Previously processed videos are saved in a library so the user can switch between video-specific chat contexts.

The Python application integrates LLMs, retrieval, background jobs, persistence, and a usable frontend and includes:

- FastAPI backend with service, repository, gateway, router, and schema boundaries.
- LangChain-based ingestion and RAG orchestration.
- OpenAI chat and embedding model integration.
- PostgreSQL persistence with pgvector-backed semantic search.
- Alembic migrations.
- Celery and Redis for long-running video processing jobs.
- Idempotent ingestion keyed by YouTube video ID.
- Cleanup of vector records when metadata persistence fails.
- Retry-aware job lifecycle with stale-job recovery.
- React/Vite single-page UI with a video library and streaming chat.
- Focused unit tests for high-risk behavior without requiring OpenAI, YouTube, or PostgreSQL.

## User Flow

1. The user enters a YouTube URL.
2. The backend creates a processing job.
3. A Celery worker loads the transcript, or falls back to audio transcription when enabled.
4. The transcript is summarized into a title/topic.
5. Transcript chunks are embedded and stored in pgvector.
6. The processed video appears in the left-side library.
7. The user chats with the video context on the right.
8. Selecting another saved video switches the chat to that video's stored history and retrieval scope.

## Architecture

```text
React/Vite UI
    |
    | HTTP + SSE
    v
FastAPI API
    |
    | enqueue job / poll status
    v
Celery Worker + Redis
    |
    | transcript/audio loading, chunking, summarization, embeddings
    v
PostgreSQL + pgvector
```

Important backend boundaries:

- `app/routers`: FastAPI API endpoints.
- `app/services`: application workflows and business rules.
- `app/repositories`: PostgreSQL access.
- `app/gateways`: external systems such as OpenAI, LangChain, pgvector, and YouTube.
- `migrations`: Alembic schema changes.
- `tests`: focused unit tests for ingestion, job lifecycle, chat guards, and RAG contracts.

## Tech Stack

- Python 3.11
- FastAPI
- Celery + Redis
- PostgreSQL + pgvector
- Alembic
- LangChain
- OpenAI chat and embeddings
- YouTube transcript API, yt-dlp, faster-whisper
- React 19, Vite, TypeScript, Tailwind CSS
- Docker Compose

## Environment

Create `.env` from the example:

```bash
cp .env.example .env
```

Required value to fill:

```env
OPENAI_API_KEY=sk-your-real-key
```

Usually safe to keep as-is for Docker:

```env
OPENAI_CHAT_MODEL=gpt-5.4-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
WHISPER_MODEL=small
DATABASE_URL=postgresql://youtube:youtube@localhost:5432/youtube_rag
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
LOG_LEVEL=INFO
ENABLE_AUDIO_FALLBACK=true
AUDIO_DOWNLOAD_DIR=.cache/audio
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
```

Notes:

- `OPENAI_API_KEY` is required for summarization, embeddings, and chat answers.
- `OPENAI_CHAT_MODEL` controls the chat/summarization model.
- `OPENAI_EMBEDDING_MODEL` controls the embedding model used by pgvector.
- `ENABLE_AUDIO_FALLBACK=true` lets the worker download audio and transcribe it when no transcript is available.
- `WHISPER_MODEL` is the local faster-whisper model used for fallback transcription.
- Docker Compose overrides database and Redis URLs inside containers so services can reach `postgres` and `redis`.

## Run With Docker

Prerequisites:

- Docker Desktop or Docker Engine with Compose.
- An OpenAI API key.

Start the full stack:

```bash
docker compose up --build
```

Open:

```text
http://localhost:5173
```

Services:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Redis: internal Compose service
- Alembic migration job: runs before backend and worker start
- Celery worker: processes video ingestion jobs

Stop the stack:

```bash
docker compose down
```

Reset local database state:

```bash
docker compose down -v
```

## Demo Script

1. Start the stack with `docker compose up --build`.
2. Open `http://localhost:5173`.
3. Paste a YouTube URL.
4. Wait for the job status to move through queued/running/succeeded.
5. Ask questions about the video.
6. Process another video.
7. Use the left-side library to switch between saved videos and continue each chat in its own context.
8. Submit the same YouTube URL again to show idempotent processing: it reuses the existing video context instead of duplicating data.

## Reliability Features

- Video ingestion is asynchronous and does not block the API request.
- Processing jobs retry transient failures up to 3 total attempts with exponential backoff.
- Queued/running jobs older than 30 minutes are marked failed as stale.
- Duplicate video submissions are scoped by YouTube video ID.
- Vector chunks written during a failed metadata insert are deleted to avoid orphan embeddings.
- Alembic owns schema changes.

## Testing

Run backend tests:

```bash
python -m unittest discover -s tests
```

Run Python syntax checks:

```bash
python -m compileall app migrations tests
```

Run frontend type checks:

```bash
cd frontend
npm run check
```

Current tests are intentionally focused on high-risk behavior:

- YouTube URL parsing.
- Ingestion idempotency and vector cleanup.
- Job retry/failure lifecycle.
- Chat service guard behavior.
- RAG retrieval scoping and transcript/audio fallback contracts.

## Local Development Without Full Docker

For backend/frontend development outside Compose, keep PostgreSQL and Redis running:

```bash
docker compose up -d postgres redis
```

Install backend dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Run the worker in another terminal:

```bash
celery -A app.tasks.celery_app worker --loglevel=info --concurrency=1
```

Run the frontend:

```bash
cd frontend
npm install
npm run dev
```

## API Overview

- `GET /api/videos`: list processed videos.
- `POST /api/videos/process`: queue or reuse processing for a YouTube URL.
- `GET /api/videos/process/active`: return the latest active processing job.
- `GET /api/videos/process/{job_id}`: poll processing status.
- `GET /api/videos/{document_id}/messages`: load chat history for a video.
- `POST /api/chat`: answer a question for a processed video.
- `POST /api/chat/stream`: stream an answer with Server-Sent Events.

## Current Limitations

- The UI is optimized for a demo workflow, not multi-user production use.
- RAG answers do not yet display citations or retrieved source snippets.
- There is no authentication or tenant isolation.
- CORS is permissive for local development.
- Audio fallback depends on YouTube availability, yt-dlp behavior, ffmpeg, and local CPU transcription speed.
