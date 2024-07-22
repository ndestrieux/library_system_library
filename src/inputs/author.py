from typing import Optional

import strawberry


@strawberry.input
class AuthorInput:
    pass

    def asdict(self):
        return {
            k: v for k, v in strawberry.asdict(self).items() if v != strawberry.UNSET
        }


@strawberry.input
class AuthorCreationInput(AuthorInput):
    first_name: str
    middle_name: Optional[str] = strawberry.UNSET
    last_name: str


@strawberry.input
class AuthorUpdateInput(AuthorInput):
    first_name: Optional[str] = strawberry.UNSET
    middle_name: Optional[str] = strawberry.UNSET
    last_name: Optional[str] = strawberry.UNSET
