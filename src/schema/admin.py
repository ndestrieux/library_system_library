from typing import List, Optional

import strawberry
from strawberry import Info

from database.crud_factory import AuthorSQLCrud, BookSQLCrud
from database.validators.author import AuthorCreateValidator, AuthorUpdateValidator
from definitions.author import AuthorAdmin
from definitions.book import BookAdmin
from filters.author import AuthorAdminFilter
from filters.book import BookAdminFilter
from inputs.author import AuthorCreationInput, AuthorUpdateInput
from permissions import HasAdminGroup, IsAuthenticated
from utils import get_requester


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated, HasAdminGroup])
    async def author_list_admin(
        self, info: Info, f: Optional[AuthorAdminFilter] = None
    ) -> List[AuthorAdmin]:
        db = info.context["db"]
        required_fields = info.selected_fields[0].selections
        authors = AuthorSQLCrud.get_many_by_values(db, required_fields, f)
        return authors

    @strawberry.field(permission_classes=[IsAuthenticated, HasAdminGroup])
    async def author_details_admin(self, info: Info, author_id: int) -> AuthorAdmin:
        db = info.context["db"]
        required_fields = info.selected_fields[0].selections
        author = AuthorSQLCrud.get_one_by_id(db, author_id, fields=required_fields)
        return author

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def book_list_admin(
        self, info: Info, f: Optional[BookAdminFilter] = None
    ) -> List[BookAdmin]:
        db = info.context["db"]
        required_fields = info.selected_fields[0].selections
        books = BookSQLCrud.get_many_by_values(db, required_fields, f)
        return books

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def book_details_admin(self, info: Info, book_id: int) -> BookAdmin:
        db = info.context["db"]
        required_fields = info.selected_fields[0].selections
        author = BookSQLCrud.get_one_by_id(db, book_id, fields=required_fields)
        return author


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated, HasAdminGroup])
    async def new_author(self, info: Info, data: AuthorCreationInput) -> AuthorAdmin:
        db = info.context["db"]
        requester = get_requester(info)
        data_dict = data.asdict() | {"created_by": requester}
        validated_data = AuthorCreateValidator(**data_dict)
        author = AuthorSQLCrud.create(db, validated_data)
        return author

    @strawberry.mutation(permission_classes=[IsAuthenticated, HasAdminGroup])
    async def modify_author(
        self, info: Info, author_id: int, data: AuthorUpdateInput
    ) -> AuthorAdmin:
        db = info.context["db"]
        requester = get_requester(info)
        required_fields = info.selected_fields[0].selections
        data_dict = data.asdict() | {"last_updated_by": requester}
        validated_data = AuthorUpdateValidator(**data_dict)
        author = AuthorSQLCrud.update_by_id(
            db, validated_data, author_id, required_fields
        )
        return author

    @strawberry.mutation(permission_classes=[IsAuthenticated, HasAdminGroup])
    async def remove_author(self, info: Info, author_id: int) -> bool:
        db = info.context["db"]
        result = AuthorSQLCrud.remove_by_id(db, author_id)
        return bool(result)
