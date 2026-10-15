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

