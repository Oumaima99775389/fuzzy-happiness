from fastapi import FastAPI
# creates the web application.
app = FastAPI(
	title="fuzzy-happiness",
	description="Backend application for the fuzzy-happiness project.",
	version="0.1.0",
)

# registers an HTTP GET endpoint.
@app.get("/healthCheck")
# handles requests to that endpoint.
def health_check():
     return {"status": "ok"}
# Returning a Python dictionary makes FastAPI return a JSON response.