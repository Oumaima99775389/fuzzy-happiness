
import sqlite3
from datetime import datetime
from pathlib import Path

from src.schemas.condition_event import ConditionEvent


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "telemetry.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_condition_event_table() -> None:
    with get_connection() as connection:
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


def find_active_event(
    device_id: str,
    journey_id: str,
    event_type: str,
) -> sqlite3.Row | None:
    with get_connection() as connection:
        return connection.execute(
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
) -> ConditionEvent:
    with get_connection() as connection:
        cursor = connection.execute(
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

    event = get_event_by_id(event_id)
    if event is None:
        raise RuntimeError("Created condition event could not be retrieved.")

    return event


def close_event(
    event_id: int,
    ended_at: datetime,
) -> ConditionEvent | None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE condition_events
            SET ended_at = ?, status = 'CLOSED'
            WHERE id = ? AND status = 'ACTIVE'
            """,
            (ended_at.isoformat(), event_id),
        )

    return get_event_by_id(event_id)


def get_event_by_id(event_id: int) -> ConditionEvent | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM condition_events WHERE id = ?",
            (event_id,),
        ).fetchone()

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


def list_events(
    device_id: str,
    journey_id: str,
    limit: int = 100,
    offset: int = 0,
) -> list[ConditionEvent]:
    with get_connection() as connection:
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

    return [
        ConditionEvent(
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
        for row in rows
    ]


initialize_condition_event_table()
