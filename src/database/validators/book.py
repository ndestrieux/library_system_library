from typing import Optional

from database.models import LanguageChoices
from database.validators.base import Validator


class BookCreateValidator(Validator):
    title: str
    publication_year: int
    language: Optional[LanguageChoices] = LanguageChoices.OTHER
    category: Optional[str] = None
    created_by: str
