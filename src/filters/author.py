from typing import Optional

import strawberry

from filters.base import AdminExtraFieldsFilter, Filter


@strawberry.input
class AuthorBasicFilter(Filter):
    first_name: Optional[str] = strawberry.UNSET
    middle_name: Optional[str] = strawberry.UNSET
    last_name: Optional[str] = strawberry.UNSET
    book_title: Optional[str] = strawberry.UNSET
    book_publication_year: Optional[int] = strawberry.UNSET


@strawberry.input
class AuthorAdminFilter(AuthorBasicFilter, AdminExtraFieldsFilter):
    pass
