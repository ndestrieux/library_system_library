from typing import Dict, Optional

from sqlalchemy import ScalarResult
from sqlalchemy.orm import Session
from strawberry import Info

from filters.author import AllAuthorFilter, OneAuthorFilter
from models import Author as AuthorModel
from query_builders import AuthorQuery
from validators.author import AuthorCreateValidator, AuthorUpdateValidator


async def get_authors(
    db: Session, info: Info, f: Optional[AllAuthorFilter]
) -> ScalarResult[AuthorModel]:
    required_fields = info.selected_fields[0].selections
    query_obj = AuthorQuery(required_fields, f)
    query = query_obj.build()
    result = db.execute(query).unique()
    return result.scalars()


async def get_author_details(
    db: Session, info: Info, f: OneAuthorFilter
) -> AuthorModel:
    required_fields = info.selected_fields[0].selections
    query_obj = AuthorQuery(required_fields, f)
    query = query_obj.build()
    result = db.execute(query).unique()
    return result.scalar()


async def create_author(db: Session, data: Dict[str, str]) -> AuthorModel:
    author_data = AuthorCreateValidator(**data)
    author = AuthorModel(**author_data.model_dump())
    db.add(author)
    db.commit()
    return author


async def update_author(
    db: Session, author_id: int, data: Dict[str, str]
) -> AuthorModel:
    author_data = AuthorUpdateValidator(**data)
    author = db.query(AuthorModel).get(author_id)
    for k, v in author_data.items():
        setattr(author, k, v)
    db.commit()
    return author
