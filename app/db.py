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
