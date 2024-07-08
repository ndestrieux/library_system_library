from fastapi import FastAPI

from database import engine
from models import Base
from routers.author import router as author_router

app = FastAPI()

app.include_router(author_router)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("Database connected on startup")


@app.on_event("shutdown")
async def shutdown():
    engine.dispose()
    print("Database disconnected on shutdown")
