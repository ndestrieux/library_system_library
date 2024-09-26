from typing import Annotated, List, Optional

from annotated_types import MinLen
from pydantic import Field, model_validator

from database.models import LanguageChoices
from database.validators.base import Validator


class BookCreateValidator(Validator):
    title: str
    authors: Annotated[List[int], MinLen(1)] = Field(exclude=True)
    publication_year: int
    language: Optional[LanguageChoices] = LanguageChoices.OTHER
    category: Optional[str] = None
    created_by: str


class BookUpdateValidator(Validator):
    title: Optional[str] = None
    add_authors: Optional[List[int]] = Field(default_factory=list, exclude=True)
    remove_authors: Optional[List[int]] = Field(default_factory=list, exclude=True)
    publication_year: Optional[int] = None
    language: Optional[LanguageChoices] = LanguageChoices.OTHER
    category: Optional[str] = None
    last_updated_by: str
    author_count: int = Field(exclude=True)

    @model_validator(mode="after")
    @classmethod
    def book_must_have_author(cls, data):
        expected_author_count = (
            data.author_count + len(data.add_authors) - len(data.remove_authors)
        )
        if data.remove_authors and expected_author_count <= 0:
            raise ValueError("Book must have at least one author")
        return data
