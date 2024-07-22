from typing import List, Optional

import strawberry
from strawberry import Info

from definitions.author import Author
from filters.author import AllAuthorFilter, OneAuthorFilter
from resolvers.author import get_author_details, get_authors


@strawberry.type
class Query:
    @strawberry.field
    async def author_list(
        self, info: Info, f: Optional[AllAuthorFilter] = None
    ) -> List[Author]:
        db = info.context["db"]
        authors = get_authors(db, info, f)
        return [Author.from_instance(author) for author in authors]

    @strawberry.field
    async def author_details(self, info: Info, f: Optional[OneAuthorFilter]) -> Author:
        db = info.context["db"]
        author = get_author_details(db, info, f)
        return Author.from_instance(author)


schema = Schema(query=Query, mutation=Mutation, extensions=[SQLAlchemySession])
