import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database.init_db import init_db
from app.routes import auth, clients, consents, dashboard, leads, proposals, simulations, tasks, whatsapp
from app.services.security import check_rate_limit

app = FastAPI(title="BBB Consig CRM API", version="0.1.0")

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
    if request.url.path.startswith(("/whatsapp", "/consultas")):
        client_ip = request.client.host if request.client else "local"
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
    init_db()


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "BBB Consig CRM API"}


app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(clients.router)
app.include_router(proposals.router)
app.include_router(tasks.router)
app.include_router(whatsapp.router)
app.include_router(simulations.router)
app.include_router(consents.router)
