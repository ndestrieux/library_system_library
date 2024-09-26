from typing import Optional

import strawberry

from filters.base import AdminExtraFieldsFilter, Filter


@strawberry.input
class BookBasicFilter(Filter):
    title: Optional[str] = strawberry.UNSET
    publication_year: Optional[int] = strawberry.UNSET
    author_first_name: Optional[str] = strawberry.UNSET
    author_middle_name: Optional[str] = strawberry.UNSET
    author_last_name: Optional[str] = strawberry.UNSET


@strawberry.input
class BookAdminFilter(BookBasicFilter, AdminExtraFieldsFilter):
    pass
