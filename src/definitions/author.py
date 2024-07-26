from datetime import date
from typing import Annotated, List, Optional

import strawberry


@strawberry.type
class AuthorBasic:
    id: int
    first_name: str
    middle_name: Optional[str]
    last_name: str
    books: List[Annotated["Book", strawberry.lazy(".book")]]


@strawberry.type
class AuthorAdmin(AuthorBasic):
    created_by: str
    created_on: date
    last_updated_by: Optional[str]
    last_updated_on: Optional[date]
