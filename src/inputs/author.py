from typing import Optional

import strawberry

from mixins import InputAsDictMixin


@strawberry.input
class AuthorCreationInput(InputAsDictMixin):
    first_name: str
    middle_name: Optional[str] = strawberry.UNSET
    last_name: str


@strawberry.input
class AuthorUpdateInput(InputAsDictMixin):
    first_name: Optional[str] = strawberry.UNSET
    middle_name: Optional[str] = strawberry.UNSET
    last_name: Optional[str] = strawberry.UNSET
