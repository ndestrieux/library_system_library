from typing import Annotated, List

import strawberry

from models import Author as AuthorModel


@strawberry.type
class Author:
    id: int
    first_name: str
    middle_name: str
    last_name: str
    books: List[Annotated["Book", strawberry.lazy(".book")]]

    @classmethod
    def from_instance(cls, model: AuthorModel) -> "Author":
        return cls(
            id=model.id,
            first_name=model.first_name,
            middle_name=model.middle_name,
            last_name=model.last_name,
            books=model.books,
        )
