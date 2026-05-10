"""FinTrack API entry point"""

from fastapi import FastAPI
from app.routers import users

# create FastAPI app instance
app = FastAPI(title="FinTrack API", version="0.1.0")
app.include_router(users.router)

@app.get("/health", summary="Health Check", description="Check if the API is running")
def health():
    return {"status": "ok"}