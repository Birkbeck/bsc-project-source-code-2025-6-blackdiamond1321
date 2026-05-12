"""FinTrack API entry point"""

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from app.routers import users
from app.routers import transactions
from app.routers import budgets
from app.routers import loans
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
@app.get("/health", summary="Health Check", description="Check if the API is running")
def health():
    return {"status": "ok"}