# Development Log

## Current status

- Day 1: Repository initialized and CI workflow passing.
- Day 2: FastAPI health endpoint implemented and tested.

## Day 1
- Goal: establish the repository and automated testing workflow.
- Result: pending.
- Next: implement and verify the first health-check test.
- steps for the set up of the test python -m pip install pytest then python -m pytest to run the test and be suer that there is no problem

## Run locally

Install dependencies:

    py -m pip install -r requirements.txt

Start the API:

    py -m uvicorn src.app:app --reload

Health endpoint: http://127.0.0.1:8000/health

Interactive documentation: http://127.0.0.1:8000/docs


## 2026-10-16 — Telemetry API foundation

- Added a versioned FastAPI telemetry endpoint.
- Separated request/response schemas, route handling, and service logic.
- Added tests for health, valid telemetry, invalid temperature, and unknown fields.
- Persistence, MQTT ingestion, authentication, and risk analysis remain unimplemented.


## Telemetry API

The Smart Transport Box backend exposes a local FastAPI interface.

### Submit telemetry

`POST /api/v1/telemetry`

Accepts a device ID, journey ID, timestamp, temperature in °C, and vibration magnitude in g. Valid readings are stored in a local SQLite database.

### Retrieve journey telemetry

`GET /api/v1/journeys/{journey_id}/telemetry`

Returns the readings recorded for the specified journey in timestamp order.

### Current limitations

- The API currently receives readings over HTTP.
- MQTT ingestion from the ESP32 is not implemented yet.
- Readings are stored locally in SQLite.
- Authentication, access control, retention policies, and risk analysis are not implemented yet.
- Prototype validation limits are not certified transport-safety thresholds.



