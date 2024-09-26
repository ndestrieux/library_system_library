from typing import Annotated, List, Optional

import strawberry

from definitions.base import AdminExtraFields


@strawberry.type
class BookBasic:
    id: int
    title: str
    authors: List[Annotated["AuthorBasic", strawberry.lazy(".author")]]
    publication_year: int
    language: str
    category: Optional[str]


@strawberry.type
class BookAdmin(BookBasic, AdminExtraFields):
    authors: List[Annotated["AuthorAdmin", strawberry.lazy(".author")]]
