from typing import List, Optional

import strawberry

from mixins import InputAsDictMixin


@strawberry.input
class BookCreationInput(InputAsDictMixin):
    title: str
    authors: List[int]
    publication_year: int
    language: Optional[str] = strawberry.UNSET
    category: Optional[str] = strawberry.UNSET


@strawberry.input
class BookUpdateInput(InputAsDictMixin):
    title: Optional[str] = strawberry.UNSET
    publication_year: Optional[int] = strawberry.UNSET
    language: Optional[str] = strawberry.UNSET
    category: Optional[str] = strawberry.UNSET
