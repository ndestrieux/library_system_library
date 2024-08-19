from datetime import date
from typing import Generic, Optional, TypeVar

import strawberry

from mixins import InputAsDictMixin


@strawberry.input
class Filter(InputAsDictMixin):
    pass


T = TypeVar("T")


@strawberry.input
class BetweenDatesFilter(Generic[T]):
    from_: date
    to_: date


@strawberry.input
class AdminExtraFieldsFilter:
    created_by: Optional[str] = strawberry.UNSET
    created_between: Optional[BetweenDatesFilter] = strawberry.UNSET
    last_updated_by: Optional[str] = strawberry.UNSET
    last_updated_between: Optional[BetweenDatesFilter] = strawberry.UNSET
