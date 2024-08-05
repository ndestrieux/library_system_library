from contextlib import asynccontextmanager

from fastapi import FastAPI
from strawberry import Schema
from strawberry.fastapi import GraphQLRouter
from strawberry.tools import merge_types

from database.db_conf import engine
from database.models import Base
from extensions import SQLAlchemySession
from schema.admin import Mutation
from schema.admin import Query as QueryAdmin
from schema.basic import Query as QueryBasic


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Database connected on startup")
    yield
    engine.dispose()
    print("Database disconnected on shutdown")


Query = merge_types("Query", (QueryBasic, QueryAdmin))

schema = Schema(query=Query, mutation=Mutation, extensions=[SQLAlchemySession])

router = GraphQLRouter(schema)

app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/graphql")
