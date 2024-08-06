from typing import Annotated, List, Optional

import strawberry

from definitions.base import AdminExtraFields


@strawberry.type
class AuthorBasic:
    id: int
    first_name: str
    middle_name: Optional[str]
    last_name: str
    books: List[Annotated["BookBasic", strawberry.lazy(".book")]]


@strawberry.type
class AuthorAdmin(AuthorBasic, AdminExtraFields):
    books: List[Annotated["BookAdmin", strawberry.lazy(".book")]]
