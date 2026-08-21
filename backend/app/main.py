from fastapi import FastAPI
from app.api.incidents import router as incidents_router

app = FastAPI(
    title="Black Box Investigator",
    description="AI-powered incident investigation system",
    version="0.1.0"
)

app.include_router(incidents_router)


@app.get("/")
def root():
    return {
        "name": "Black Box Investigator",
        "status": "online",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }