from app.db_infra import get_conn


def list_messages(video_id: str) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, role, content, created_at
            FROM chat_messages
            WHERE video_id = %s
            ORDER BY id ASC
            """,
            (video_id,),
        ).fetchall()
    return list(rows)


def add_message(video_id: str, role: str, content: str) -> dict:
    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO chat_messages (video_id, role, content)
            VALUES (%s, %s, %s)
            RETURNING id, role, content, created_at
            """,
            (video_id, role, content),
        ).fetchone()
        conn.commit()
    assert row is not None
    return row
