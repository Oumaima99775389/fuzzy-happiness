
import sqlite3
from datetime import datetime
from pathlib import Path

from src.schemas.telemetry import TelemetryRequest

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "telemetry.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                journey_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                temperature_c REAL NOT NULL,
                vibration_g REAL NOT NULL
            )
            """
        )


def save_telemetry(telemetry: TelemetryRequest) -> int:
    initialize_database()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO telemetry (
                device_id,
                journey_id,
                timestamp,
                temperature_c,
                vibration_g
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                telemetry.device_id,
                telemetry.journey_id,
                telemetry.timestamp.isoformat(),
                telemetry.temperature_c,
                telemetry.vibration_g,
            ),
        )
        return cursor.lastrowid


def get_telemetry_for_journey(journey_id: str) -> list[dict]:
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                device_id,
                journey_id,
                timestamp,
                temperature_c,
                vibration_g
            FROM telemetry
            WHERE journey_id = ?
            ORDER BY timestamp ASC, id ASC
            """,
            (journey_id,),
        ).fetchall()

    return [dict(row) for row in rows]
