"""Dastur kirish nuqtasi: uvicorn app.main:app"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401  (jadvallar ro'yxatga olinishi uchun)
from .database import Base, SessionLocal, engine
from .routers import calls, chat
from .seed import seed_units


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)          # jadvallarni yaratadi
    with SessionLocal() as db:
        seed_units(db)                        # namunaviy brigadalar
    yield


app = FastAPI(title="Smart SOS", version="0.1.0", lifespan=lifespan)

# Frontend boshqa manzildan so'rov yuborishi uchun. Ishlab chiqarishda "*" ni almashtiring.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"],
                   allow_headers=["*"])

app.include_router(calls.router)
app.include_router(chat.router)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
