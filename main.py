from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import Base, engine
import app.models  # noqa: F401 — registers all models with Base before create_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Dietitian Management Panel", lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Dietitian Management Panel API"}
