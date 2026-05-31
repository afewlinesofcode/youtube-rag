import uuid

from app.db_infra import get_conn


ACTIVE_JOB_MAX_AGE_MINUTES = 30


def get_active_process_job(*, max_age_minutes: int = ACTIVE_JOB_MAX_AGE_MINUTES) -> dict | None:
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT id::text, youtube_url, status, video_id::text, error, created_at, updated_at
            FROM process_jobs
            WHERE status IN ('queued', 'running')
              AND COALESCE(updated_at, created_at) >= now() - make_interval(mins => %s)
            ORDER BY COALESCE(updated_at, created_at) DESC
            LIMIT 1
            """,
            (max_age_minutes,),
        ).fetchone()


def create_process_job(youtube_url: str) -> dict:
    job_id = str(uuid.uuid4())
    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO process_jobs (id, youtube_url, status)
            VALUES (%s, %s, 'queued')
            RETURNING id::text, youtube_url, status, video_id::text, error, created_at, updated_at
            """,
            (job_id, youtube_url),
        ).fetchone()
        conn.commit()
    assert row is not None
    return row


def get_process_job(job_id: str) -> dict | None:
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT id::text, youtube_url, status, video_id::text, error, created_at, updated_at
            FROM process_jobs
            WHERE id = %s
            """,
            (job_id,),
        ).fetchone()


def mark_process_job_running(job_id: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE process_jobs
            SET status = 'running', error = NULL, updated_at = now()
            WHERE id = %s
            """,
            (job_id,),
        )
        conn.commit()


def mark_process_job_succeeded(job_id: str, video_id: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE process_jobs
            SET status = 'succeeded', video_id = %s, error = NULL, updated_at = now()
            WHERE id = %s
            """,
            (video_id, job_id),
        )
        conn.commit()


def mark_process_job_failed(job_id: str, error: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE process_jobs
            SET status = 'failed', error = %s, updated_at = now()
            WHERE id = %s
            """,
            (error[:2000], job_id),
        )
        conn.commit()
