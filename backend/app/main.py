from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.init_db import init_db
from app.routes import clients, dashboard, leads, proposals, simulations, tasks, whatsapp

app = FastAPI(title="BBB Consig CRM API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "BBB Consig CRM API"}


app.include_router(dashboard.router)
app.include_router(leads.router)
app.include_router(clients.router)
app.include_router(proposals.router)
app.include_router(tasks.router)
app.include_router(whatsapp.router)
app.include_router(simulations.router)
