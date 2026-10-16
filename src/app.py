from fastapi import FastAPI
from src.api.routes.telemetry import router as telemetry_router  # imports the telemetry router from the telemetry module.
# creates the web application.
app = FastAPI(
	title="fuzzy-happiness",
	description="Backend application for the fuzzy-happiness project.",
	version="0.1.0",
)

app.include_router(telemetry_router)  # includes the telemetry router in the application.

# registers an HTTP GET endpoint.
@app.get("/healthCheck")
# handles requests to that endpoint.
def health_check():
     return {"status": "ok"}
# Returning a Python dictionary makes FastAPI return a JSON response.