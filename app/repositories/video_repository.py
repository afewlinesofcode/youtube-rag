from app.db import get_conn


def list_videos() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id::text, youtube_url, youtube_video_id, title, topic, created_at
            FROM videos
            ORDER BY created_at DESC
            """
        ).fetchall()
    return list(rows)


def get_video(video_id: str) -> dict | None:
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT id::text, youtube_url, youtube_video_id, title, topic, created_at
            FROM videos
            WHERE id = %s
            """,
            (video_id,),
        ).fetchone()


def get_video_by_youtube_video_id(youtube_video_id: str) -> dict | None:
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT id::text, youtube_url, youtube_video_id, title, topic, created_at
            FROM videos
            WHERE youtube_video_id = %s
            """,
            (youtube_video_id,),
        ).fetchone()


def create_video(video_id: str, youtube_url: str, youtube_video_id: str, title: str, topic: str) -> dict:
    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO videos (id, youtube_url, youtube_video_id, title, topic)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id::text, youtube_url, youtube_video_id, title, topic, created_at
            """,
            (video_id, youtube_url, youtube_video_id, title, topic),
        ).fetchone()
        conn.commit()
    assert row is not None
    return row
