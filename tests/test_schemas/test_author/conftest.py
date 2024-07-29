import pytest

from database.validators.author import AuthorCreateValidator
from src.database.crud_factory import AuthorSQLCrud


@pytest.fixture(scope="function")
def author_validated_data_list():
    return [
        AuthorCreateValidator(
            first_name="Dale", last_name="Cooper", created_by="admin1"
        ),
        AuthorCreateValidator(
            first_name="Gordon", last_name="Cole", created_by="admin1"
        ),
        AuthorCreateValidator(
            first_name="John",
            middle_name="Ronald Reuel",
            last_name="Tolkien",
            created_by="admin1",
        ),
    ]


@pytest.fixture(scope="function")
def populate_db(db_session, author_validated_data_list):
    for author in author_validated_data_list:
        AuthorSQLCrud.create(db_session, author)
