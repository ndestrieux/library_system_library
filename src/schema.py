from typing import List, Optional

import strawberry
from strawberry import Info

from definitions.author import Author
from filters.author import AuthorFilter
from resolvers.author import get_authors


@strawberry.type
class Query:
    @strawberry.field
    async def author_list(
        self, info: Info, f: Optional[AuthorFilter] = None
    ) -> List[Author]:
        db = info.context["db"]
        authors = get_authors(db, info, f)
        return [Author.from_instance(author) for author in authors]
