from typing import Optional

import strawberry

from mixins import InputAsDictMixin


@strawberry.input
class Filter(InputAsDictMixin):
    pass


@strawberry.input
class AllAuthorFilter(Filter):
    first_name: Optional[str] = strawberry.UNSET
    middle_name: Optional[str] = strawberry.UNSET
    last_name: Optional[str] = strawberry.UNSET
    book_title: Optional[str] = strawberry.UNSET
