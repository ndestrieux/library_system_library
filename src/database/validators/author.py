from typing import Optional

from database.validators.base import Validator


class AuthorCreateValidator(Validator):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    created_by: str


class AuthorUpdateValidator(Validator):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    last_updated_by: str
