from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import engine
from models import Base
from routers.author import router as author_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Database connected on startup")
    yield
    engine.dispose()
    print("Database disconnected on shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(author_router)
