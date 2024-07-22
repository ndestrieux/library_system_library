from typing import List, Optional

import strawberry
from strawberry import Info, Schema

from definitions.author import Author
from extensions import SQLAlchemySession
from filters.author import AllAuthorFilter, OneAuthorFilter
from inputs.author import AuthorCreationInput, AuthorUpdateInput
from resolvers.author import (
    create_author,
    get_author_details,
    get_authors,
    update_author,
)
from utils import get_requester


@strawberry.type
class Query:
    @strawberry.field
    async def author_list(
        self, info: Info, f: Optional[AllAuthorFilter] = None
    ) -> List[Author]:
        db = info.context["db"]
        authors = await get_authors(db, info, f)
        return [Author.from_instance(author) for author in authors]

    @strawberry.field
    async def author_details(self, info: Info, f: Optional[OneAuthorFilter]) -> Author:
        db = info.context["db"]
        author = await get_author_details(db, info, f)
        return Author.from_instance(author)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def new_author(self, info: Info, data: AuthorCreationInput) -> Author:
        db = info.context["db"]
        requester = get_requester(info)
        data_dict = data.asdict() | {"created_by": requester}
        author = await create_author(db, data_dict)
        return Author.from_instance(author)

    @strawberry.mutation
    async def modify_author(
        self, info: Info, author_id: int, data: AuthorUpdateInput
    ) -> Author:
        db = info.context["db"]
        requester = get_requester(info)
        data_dict = data.asdict() | {"last_updated_by": requester}
        author = await update_author(db, author_id, data_dict)
        return Author.from_instance(author)


schema = Schema(query=Query, mutation=Mutation, extensions=[SQLAlchemySession])
