from typing import Optional

from sqlalchemy import ScalarResult
from sqlalchemy.orm import Session
from strawberry import Info

from filters.author import AllAuthorFilter, OneAuthorFilter
from models import Author as AuthorModel
from query_builders import AuthorQuery


def get_authors(
    db: Session, info: Info, f: Optional[AllAuthorFilter]
) -> ScalarResult[AuthorModel]:
    required_fields = info.selected_fields[0].selections
    query_obj = AuthorQuery(required_fields, f)
    query = query_obj.build()
    result = db.execute(query).unique()
    return result.scalars()


def get_author_details(db: Session, info: Info, f: OneAuthorFilter) -> AuthorModel:
    required_fields = info.selected_fields[0].selections
    query_obj = AuthorQuery(required_fields, f)
    query = query_obj.build()
    result = db.execute(query).unique()
    return result.scalar()
