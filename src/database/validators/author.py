from typing import Optional, TypeAlias

from pydantic import BaseModel

Validator: TypeAlias = BaseModel


class AuthorCreateValidator(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    created_by: str


class AuthorUpdateValidator(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    last_updated_by: str
