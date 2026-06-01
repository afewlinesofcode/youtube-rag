import uuid

from psycopg.errors import UniqueViolation

from app.db import get_conn


ACTIVE_JOB_MAX_AGE_MINUTES = 30
DEFAULT_MAX_ATTEMPTS = 3
STALE_JOB_MAX_AGE_MINUTES = 30

JOB_COLUMNS = """
    id::text,
    youtube_url,
    youtube_video_id,
    status,
    video_id::text,
    error,
    created_at,
    updated_at,
    attempt_count,
    max_attempts,
    started_at,
    finished_at,
    last_error,
    failure_reason
"""


def get_active_process_job(*, max_age_minutes: int = ACTIVE_JOB_MAX_AGE_MINUTES) -> dict | None:
    mark_stale_process_jobs_failed()
    with get_conn() as conn:
        return conn.execute(
            f"""
            SELECT {JOB_COLUMNS}
            FROM process_jobs
            WHERE status IN ('queued', 'running')
              AND COALESCE(updated_at, created_at) >= now() - make_interval(mins => %s)
            ORDER BY COALESCE(updated_at, created_at) DESC
            LIMIT 1
            """,
            (max_age_minutes,),
        ).fetchone()


def get_active_process_job_by_youtube_video_id(youtube_video_id: str) -> dict | None:
    mark_stale_process_jobs_failed()
    with get_conn() as conn:
        return conn.execute(
            f"""
            SELECT {JOB_COLUMNS}
            FROM process_jobs
            WHERE youtube_video_id = %s
              AND status IN ('queued', 'running')
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (youtube_video_id,),
        ).fetchone()


def create_process_job(youtube_url: str, youtube_video_id: str) -> dict:
    mark_stale_process_jobs_failed()
    job_id = str(uuid.uuid4())
    with get_conn() as conn:
        try:
            row = conn.execute(
                f"""
                INSERT INTO process_jobs (id, youtube_url, youtube_video_id, status, max_attempts)
                VALUES (%s, %s, %s, 'queued', %s)
                RETURNING {JOB_COLUMNS}
                """,
                (job_id, youtube_url, youtube_video_id, DEFAULT_MAX_ATTEMPTS),
            ).fetchone()
            conn.commit()
        except UniqueViolation:
            conn.rollback()
            row = get_active_process_job_by_youtube_video_id(youtube_video_id)
            if row is not None:
                return row
            return create_process_job(youtube_url, youtube_video_id)
    assert row is not None
    return row


def create_succeeded_process_job(youtube_url: str, youtube_video_id: str, video_id: str) -> dict:
    job_id = str(uuid.uuid4())
    with get_conn() as conn:
        row = conn.execute(
            f"""
            INSERT INTO process_jobs (
                id, youtube_url, youtube_video_id, status, video_id, max_attempts, finished_at
            )
            VALUES (%s, %s, %s, 'succeeded', %s, %s, now())
            RETURNING {JOB_COLUMNS}
            """,
            (job_id, youtube_url, youtube_video_id, video_id, DEFAULT_MAX_ATTEMPTS),
        ).fetchone()
        conn.commit()
    assert row is not None
    return row


def get_process_job(job_id: str) -> dict | None:
    with get_conn() as conn:
        return conn.execute(
            f"""
            SELECT {JOB_COLUMNS}
            FROM process_jobs
            WHERE id = %s
            """,
            (job_id,),
        ).fetchone()


def mark_process_job_running(job_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            f"""
            UPDATE process_jobs
            SET status = 'running',
                attempt_count = attempt_count + 1,
                error = NULL,
                failure_reason = NULL,
                started_at = COALESCE(started_at, now()),
                updated_at = now()
            WHERE id = %s
              AND status IN ('queued', 'running')
            RETURNING {JOB_COLUMNS}
            """,
            (job_id,),
        ).fetchone()
        conn.commit()
    return row


def mark_process_job_retryable_failure(job_id: str, error: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE process_jobs
            SET status = 'queued',
                error = NULL,
                last_error = %s,
                failure_reason = 'transient_error',
                updated_at = now()
            WHERE id = %s
            """,
            (error[:2000], job_id),
        )
        conn.commit()


def mark_process_job_succeeded(job_id: str, video_id: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE process_jobs
            SET status = 'succeeded',
                video_id = %s,
                error = NULL,
                last_error = NULL,
                failure_reason = NULL,
                finished_at = now(),
                updated_at = now()
            WHERE id = %s
            """,
            (video_id, job_id),
        )
        conn.commit()


def mark_process_job_failed(job_id: str, error: str, failure_reason: str = "permanent_error") -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE process_jobs
            SET status = 'failed',
                error = %s,
                last_error = %s,
                failure_reason = %s,
                finished_at = now(),
                updated_at = now()
            WHERE id = %s
            """,
            (error[:2000], error[:2000], failure_reason, job_id),
        )
        conn.commit()


def mark_stale_process_jobs_failed(*, max_age_minutes: int = STALE_JOB_MAX_AGE_MINUTES) -> int:
    with get_conn() as conn:
        result = conn.execute(
            """
            UPDATE process_jobs
            SET status = 'failed',
                error = 'Processing timed out. Please submit the video again.',
                last_error = 'Processing timed out. Please submit the video again.',
                failure_reason = 'stale_timeout',
                finished_at = now(),
                updated_at = now()
            WHERE status IN ('queued', 'running')
              AND COALESCE(started_at, updated_at, created_at) < now() - make_interval(mins => %s)
            """,
            (max_age_minutes,),
        )
        conn.commit()
    return result.rowcount or 0
