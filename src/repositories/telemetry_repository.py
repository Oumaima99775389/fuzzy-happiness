
import sqlite3
from datetime import datetime
from pathlib import Path

from src.schemas.telemetry import TelemetryRequest

# This module provides functions to interact with the telemetry database.
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "telemetry.db"

# Establishes a connection to the SQLite database and ensures the database file exists.
def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

# Initializes the telemetry database by creating the telemetry table if it doesn't exist.
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

# Saves a telemetry record to the database and returns the ID of the inserted record.
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
    
# Retrieves telemetry records for a specific journey from the database and returns them as a list of dictionaries.
def get_telemetry_for_journey(
    journey_id: str,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id, device_id, journey_id, timestamp,
                temperature_c, vibration_g
            FROM telemetry
            WHERE journey_id = ?
            ORDER BY timestamp ASC, id ASC
            LIMIT ? OFFSET ?
            """,
            (journey_id, limit, offset),
        ).fetchall()

    return [dict(row) for row in rows]

# Retrieves telemetry records for a specific device from the database and returns them as a list of dictionaries.
def get_telemetry_for_device(
    device_id: str,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id, device_id, journey_id, timestamp,
                temperature_c, vibration_g
            FROM telemetry
            WHERE device_id = ?
            ORDER BY timestamp ASC, id ASC
            LIMIT ? OFFSET ?
            """,
            (device_id, limit, offset),
        ).fetchall()

    return [dict(row) for row in rows]


def get_telemetry_for_device_journey(
    device_id: str,
    journey_id: str,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id, device_id, journey_id, timestamp,
                temperature_c, vibration_g
            FROM telemetry
            WHERE device_id = ? AND journey_id = ?
            ORDER BY timestamp ASC, id ASC
            LIMIT ? OFFSET ?
            """,
            (device_id, journey_id, limit, offset),
        ).fetchall()

    return [dict(row) for row in rows]



