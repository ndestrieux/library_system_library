from typing import Optional

from sqlalchemy.orm import Session
from strawberry import Info

from filters.author import AuthorFilter
from models import Author as AuthorModel
from query_builders import AuthorQuery


def get_authors(db: Session, info: Info, f: Optional[AuthorFilter]):
    required_fields = info.selected_fields[0].selections
    query_obj = AuthorQuery(AuthorModel, required_fields, f)
    query = query_obj.build()
    result = db.execute(query).unique()
    return result.scalars()
