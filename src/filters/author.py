from typing import Optional

import strawberry


class AuthorFilter:
    pass


@strawberry.input
class AllAuthorFilter(AuthorFilter):
    first_name: Optional[str] = strawberry.UNSET
    middle_name: Optional[str] = strawberry.UNSET
    last_name: Optional[str] = strawberry.UNSET
    book_title: Optional[str] = strawberry.UNSET


@strawberry.input
class OneAuthorFilter(AuthorFilter):
    id: Optional[int] = strawberry.UNSET
