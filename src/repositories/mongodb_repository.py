import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

# Load configuration from the project's root .env file.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

_client = None


def get_mongodb_database():
    global _client

    uri = os.getenv("MONGODB_URI")
    database_name = os.getenv(
        "MONGODB_DATABASE",
        "fuzzy_happiness_DB",
    )

    if not uri:
        raise RuntimeError("MONGODB_URI is missing from .env")

    if _client is None:
        _client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,
        )

    return _client[database_name]


def save_telemetry(telemetry, sqlite_id: int) -> None:
    """Save a telemetry reading to MongoDB, without duplicating its SQLite ID."""

    database = get_mongodb_database()

    document = telemetry.model_dump(mode="python")
    document["sqlite_id"] = sqlite_id

    database["telemetry"].update_one(
        {"sqlite_id": sqlite_id},
        {"$set": document},
        upsert=True,
    )
