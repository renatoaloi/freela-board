from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from sqlalchemy import text

from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE clientes ADD COLUMN cep VARCHAR(9) NOT NULL DEFAULT ''"))
            conn.commit()
    except Exception:
        pass
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="FreelaBoard API",
    description="FreelaBoard - Freelance Project Management Backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(api_router)
