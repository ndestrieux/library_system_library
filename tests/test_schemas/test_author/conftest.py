from datetime import date

import pytest
from freezegun import freeze_time

from database.validators.author import AuthorCreateValidator
from src.database.crud_factory import AuthorSQLCrud


@pytest.fixture(scope="function")
def author_validated_data_list():
    return [
        AuthorCreateValidator(
            first_name="Dale", last_name="Cooper", created_by="test_admin"
        ),
        AuthorCreateValidator(
            first_name="Gordon", last_name="Cole", created_by="test_admin"
        ),
        AuthorCreateValidator(
            first_name="John",
            middle_name="Ronald Reuel",
            last_name="Tolkien",
            created_by="test_admin",
        ),
    ]


@pytest.fixture(scope="function")
def populate_db(db_session, author_validated_data_list):
    dates = (date(2024, month, 1) for month in range(1, 4))
    for author in author_validated_data_list:
        with freeze_time(dates):
            AuthorSQLCrud.create(db_session, author)
            db_session.commit()
