
import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime
from pathlib import Path
from collections.abc import Iterator

from src.schemas.condition_event import ConditionEvent


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "telemetry.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def _use_connection(
    connection: sqlite3.Connection | None,
) -> Iterator[sqlite3.Connection]:
    """Reuse a supplied connection or manage a standalone connection."""
    if connection is not None:
        yield connection
        return

    with closing(get_connection()) as owned_connection:
        with owned_connection:
            yield owned_connection


def initialize_condition_event_table() -> None:
    with _use_connection(None) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS condition_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                journey_id TEXT NOT NULL,
                event_type TEXT NOT NULL CHECK (
                    event_type IN ('TEMPERATURE_HIGH', 'TEMPERATURE_LOW')
                ),
                started_at TEXT NOT NULL,
                ended_at TEXT,
                status TEXT NOT NULL CHECK (
                    status IN ('ACTIVE', 'CLOSED')
                )
            )
            """
        )


def _row_to_event(row: sqlite3.Row | None) -> ConditionEvent | None:
    if row is None:
        return None

    return ConditionEvent(
        id=row["id"],
        device_id=row["device_id"],
        journey_id=row["journey_id"],
        event_type=row["event_type"],
        started_at=datetime.fromisoformat(row["started_at"]),
        ended_at=(
            datetime.fromisoformat(row["ended_at"])
            if row["ended_at"] is not None
            else None
        ),
        status=row["status"],
    )


def find_active_event(
    device_id: str,
    journey_id: str,
    event_type: str,
    connection: sqlite3.Connection | None = None,
) -> sqlite3.Row | None:
    with _use_connection(connection) as db:
        return db.execute(
            """
            SELECT *
            FROM condition_events
            WHERE device_id = ?
              AND journey_id = ?
              AND event_type = ?
              AND status = 'ACTIVE'
            ORDER BY started_at DESC
            LIMIT 1
            """,
            (device_id, journey_id, event_type),
        ).fetchone()


def create_event(
    device_id: str,
    journey_id: str,
    event_type: str,
    started_at: datetime,
    connection: sqlite3.Connection | None = None,
) -> ConditionEvent:
    with _use_connection(connection) as db:
        cursor = db.execute(
            """
            INSERT INTO condition_events (
                device_id,
                journey_id,
                event_type,
                started_at,
                ended_at,
                status
            )
            VALUES (?, ?, ?, ?, NULL, 'ACTIVE')
            """,
            (
                device_id,
                journey_id,
                event_type,
                started_at.isoformat(),
            ),
        )

        event_id = cursor.lastrowid
        event = _row_to_event(
            db.execute(
                "SELECT * FROM condition_events WHERE id = ?",
                (event_id,),
            ).fetchone()
        )

        if event is None:
            raise RuntimeError(
                "Created condition event could not be retrieved."
            )

        return event


def close_event(
    event_id: int,
    ended_at: datetime,
    connection: sqlite3.Connection | None = None,
) -> ConditionEvent | None:
    with _use_connection(connection) as db:
        db.execute(
            """
            UPDATE condition_events
            SET ended_at = ?, status = 'CLOSED'
            WHERE id = ? AND status = 'ACTIVE'
            """,
            (ended_at.isoformat(), event_id),
        )

        row = db.execute(
            "SELECT * FROM condition_events WHERE id = ?",
            (event_id,),
        ).fetchone()

        return _row_to_event(row)


def get_event_by_id(
    event_id: int,
    connection: sqlite3.Connection | None = None,
) -> ConditionEvent | None:
    with _use_connection(connection) as db:
        row = db.execute(
            "SELECT * FROM condition_events WHERE id = ?",
            (event_id,),
        ).fetchone()

        return _row_to_event(row)


def list_events(
    device_id: str,
    journey_id: str,
    limit: int = 100,
    offset: int = 0,
) -> list[ConditionEvent]:
    with _use_connection(None) as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM condition_events
            WHERE device_id = ? AND journey_id = ?
            ORDER BY started_at DESC
            LIMIT ? OFFSET ?
            """,
            (device_id, journey_id, limit, offset),
        ).fetchall()

    return [_row_to_event(row) for row in rows if row is not None]


initialize_condition_event_table()


def get_journey_event_summary(journey_id: str) -> dict[str, int]:
    with _use_connection(None) as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(CASE
                    WHEN event_type = 'TEMPERATURE_HIGH'
                    THEN 1
                END) AS high_temperature,
                COUNT(CASE
                    WHEN event_type = 'TEMPERATURE_LOW'
                    THEN 1
                END) AS low_temperature,
                COUNT(CASE
                    WHEN status = 'ACTIVE'
                    THEN 1
                END) AS active
            FROM condition_events
            WHERE journey_id = ?
            """,
            (journey_id,),
        ).fetchone()

    return {
        "high_temperature": row["high_temperature"],
        "low_temperature": row["low_temperature"],
        "active": row["active"],
    }

