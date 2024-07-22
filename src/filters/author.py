from typing import Optional

import strawberry

from mixins import InputAsDictMixin


class Filter:
    pass


@strawberry.input
class AllAuthorFilter(InputAsDictMixin, Filter):
    first_name: Optional[str] = strawberry.UNSET
    middle_name: Optional[str] = strawberry.UNSET
    last_name: Optional[str] = strawberry.UNSET
    book_title: Optional[str] = strawberry.UNSET
