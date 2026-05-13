"""FinTrack API entry point"""
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import users
from app.routers import transactions
from app.routers import budgets
from app.routers import loans
from app.routers import summary
from app.routers import payment_sources
from app.utils.exceptions import DomainError

# create FastAPI app instance
app = FastAPI(title="FinTrack API", version="0.1.0")


@app.exception_handler(DomainError)
async def domain_error(request: Request, exc: DomainError) -> JSONResponse:
    """Catch any DomainError raised by services"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(loans.router)
app.include_router(summary.router)
app.include_router(payment_sources.router)

# Linking frontend files

# Paths to frontend files
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
FRONTEND = os.path.join(PROJECT_ROOT, "frontend")
PUBLIC_PAGES = os.path.join(FRONTEND, "templates", "public")
PRIVATE_PAGES = os.path.join(FRONTEND, "templates", "private")
IMAGES = os.path.join(PROJECT_ROOT, "images")
MODALS = os.path.join(FRONTEND, "templates", "modals")

# Mount to static folder
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND, "static")), name="static")

# Mount to images folder
app.mount("/images", StaticFiles(directory=IMAGES), name="images")


@app.get("/")
def landing():
    """Landing page"""
    return FileResponse(os.path.join(PUBLIC_PAGES, "index.html"))

@app.get("/modals/{name}")
def modal(name: str):
    """Modals templates"""
    safe_name = os.path.basename(name)
    path = os.path.join(MODALS, f"{safe_name}.html")
    if not os.path.isfile(path):
        return JSONResponse(status_code=404, content={"detail": "Modal not found"})
    return FileResponse(path)

@app.get("/dashboard")
def dashboard():
    """Dashboard page. Auth check is client-side in dashboard.js"""
    return FileResponse(os.path.join(PRIVATE_PAGES, "dashboard.html"))

@app.get("/health", summary="Health Check", description="Check if the API is running")
def health():
    return {"status": "ok"}