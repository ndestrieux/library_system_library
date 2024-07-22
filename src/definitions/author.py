from typing import Annotated, List, Optional

import strawberry

from database.models import Author as AuthorModel


@strawberry.type
class Author:
    id: int
    first_name: str
    middle_name: Optional[str]
    last_name: str
    books: List[Annotated["Book", strawberry.lazy(".book")]]

    @classmethod
    def from_instance(cls, obj: AuthorModel) -> "Author":
        return cls(
            id=obj.id,
            first_name=obj.first_name,
            middle_name=obj.middle_name,
            last_name=obj.last_name,
            books=obj.books,
        )
