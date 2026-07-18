import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config.environment import validate_environment
from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.routes import auth, clients, consents, dashboard, leads, proposals, simulations, tasks, whatsapp
from app.services.security import check_rate_limit

APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")
app = FastAPI(title="BBB Consig CRM API", version=APP_VERSION)

DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_and_limits(request: Request, call_next):
    client_ip = request.client.host if request.client else "local"
    if request.url.path != "/healthz":
        try:
            check_rate_limit(f"global:{client_ip}", limit=300, window_seconds=60)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    if request.url.path.startswith(("/whatsapp", "/consultas")):
        try:
            check_rate_limit(f"sensitive:{client_ip}:{request.url.path}", limit=60, window_seconds=60)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
    return response


@app.on_event("startup")
def on_startup() -> None:
    validate_environment()
    init_db()


@app.get("/healthz")
def healthz():
    db_status = "ok"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "service": "BBB Consig CRM API",
        "version": APP_VERSION,
        "database": db_status,
        "environment": os.environ.get("APP_MODE", "demo"),
    }


app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(clients.router)
app.include_router(proposals.router)
app.include_router(tasks.router)
app.include_router(whatsapp.router)
app.include_router(simulations.router)
app.include_router(consents.router)
