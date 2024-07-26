from typing import List, Optional

import strawberry
from strawberry import Info

from database.crud_factory import AuthorSQLCrud
from definitions.author import AuthorBasic
from filters.author import AuthorBasicFilter
from permissions import IsAuthenticated


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def author_list(
        self, info: Info, f: Optional[AuthorBasicFilter] = None
    ) -> List[AuthorBasic]:
        db = info.context["db"]
        required_fields = info.selected_fields[0].selections
        authors = AuthorSQLCrud.get_many_by_values(db, required_fields, f)
        return authors

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def author_details(self, info: Info, author_id: int) -> AuthorBasic:
        db = info.context["db"]
        required_fields = info.selected_fields[0].selections
        author = AuthorSQLCrud.get_one_by_id(db, author_id, fields=required_fields)
        return author
