from typing import List, Optional

import strawberry
from strawberry import Info, Schema

from database.crud_factory import crud_factory
from database.models import Author as AuthorModel
from database.validators.author import AuthorCreateValidator, AuthorUpdateValidator
from definitions.author import Author
from extensions import SQLAlchemySession
from filters.author import AllAuthorFilter
from inputs.author import AuthorCreationInput, AuthorUpdateInput
from utils import get_requester

AuthorCrud = crud_factory(AuthorModel)


@strawberry.type
class Query:
    @strawberry.field
    async def author_list(
        self, info: Info, f: Optional[AllAuthorFilter] = None
    ) -> List[Author]:
        db = info.context["db"]
        required_fields = info.selected_fields[0].selections
        authors = AuthorCrud.get_many_by_values(db, required_fields, f)
        return [Author.from_instance(author) for author in authors]

    @strawberry.field
    async def author_details(self, info: Info, author_id: int) -> Author:
        db = info.context["db"]
        required_fields = info.selected_fields[0].selections
        author = AuthorCrud.get_one_by_id(db, author_id, fields=required_fields)
        return Author.from_instance(author)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def new_author(self, info: Info, data: AuthorCreationInput) -> Author:
        db = info.context["db"]
        requester = get_requester(info)
        data_dict = data.asdict() | {"created_by": requester}
        validated_data = AuthorCreateValidator(**data_dict)
        author = AuthorCrud.create(db, validated_data)
        return Author.from_instance(author)

    @strawberry.mutation
    async def modify_author(
        self, info: Info, author_id: int, data: AuthorUpdateInput
    ) -> Author:
        db = info.context["db"]
        requester = get_requester(info)
        data_dict = data.asdict() | {"last_updated_by": requester}
        validated_data = AuthorUpdateValidator(**data_dict)
        author = AuthorCrud.update_by_id(db, validated_data, author_id)
        return Author.from_instance(author)

    @strawberry.mutation
    async def remove_author(self, info: Info, author_id: int) -> bool:
        db = info.context["db"]
        result = AuthorCrud.remove_by_id(db, author_id)
        return result


schema = Schema(query=Query, mutation=Mutation, extensions=[SQLAlchemySession])
