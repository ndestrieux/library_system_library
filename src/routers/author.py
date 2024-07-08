from strawberry import Schema
from strawberry.fastapi import GraphQLRouter

from extensions import SQLAlchemySession
from schema import Query

schema = Schema(query=Query, extensions=[SQLAlchemySession])


router = GraphQLRouter(schema, prefix="/api/library/authors", tags=["authors"])
