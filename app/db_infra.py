from collections.abc import Iterator
from contextlib import contextmanager

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import get_settings


pool: ConnectionPool | None = None


def init_pool() -> None:
    global pool
    if pool is None:
        settings = get_settings()
        pool = ConnectionPool(
            conninfo=settings.psycopg_connection_url,
            kwargs={"row_factory": dict_row},
            min_size=1,
            max_size=8,
            open=True,
        )


def close_pool() -> None:
    global pool
    if pool is not None:
        pool.close()
        pool = None


@contextmanager
def get_conn() -> Iterator[Connection]:
    if pool is None:
        init_pool()
    assert pool is not None
    with pool.connection() as conn:
        yield conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS videos (
                id UUID PRIMARY KEY,
                youtube_url TEXT NOT NULL,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id BIGSERIAL PRIMARY KEY,
                video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS process_jobs (
                id UUID PRIMARY KEY,
                youtube_url TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'succeeded', 'failed')),
                video_id UUID REFERENCES videos(id) ON DELETE SET NULL,
                error TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        conn.commit()
