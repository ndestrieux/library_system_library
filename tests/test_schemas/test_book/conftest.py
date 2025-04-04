from datetime import date

import pytest
from freezegun import freeze_time
from strawberry.types.nodes import SelectedField

from database.models import LanguageChoices
from database.validators.author import AuthorCreateValidator
from database.validators.book import BookCreateValidator
from src.database.crud_factory import AuthorSQLCrud, BookSQLCrud


@pytest.fixture(scope="session")
def selected_fields():
    return [SelectedField(name="id", arguments={}, directives={}, selections=[])]


@pytest.fixture(scope="function")
def author_validated_data_list():
    return [
        AuthorCreateValidator(
            first_name="Bram", last_name="Stoker", created_by="test_admin"
        ),
        AuthorCreateValidator(
            first_name="Louis-Ferdinand", last_name="Céline", created_by="test_admin"
        ),
        AuthorCreateValidator(
            first_name="John",
            middle_name="Ronald Reuel",
            last_name="Tolkien",
            created_by="test_admin",
        ),
    ]


@pytest.fixture(scope="function")
def book_data_list(db_session):
    return [
        {
            "title": "Dracula",
            "authors": [1],
            "publication_year": 1897,
            "language": LanguageChoices.EN,
            "category": "Horror",
            "created_by": "test_admin",
        },
        {
            "title": "Voyage au bout de la nuit",
            "authors": [2],
            "publication_year": 1932,
            "language": LanguageChoices.FR,
            "category": "Novel",
            "created_by": "test_admin",
        },
        {
            "title": "The Hobbit",
            "authors": [3],
            "publication_year": 1937,
            "language": LanguageChoices.EN,
            "category": "Fantasy",
            "created_by": "test_admin",
        },
    ]


@pytest.fixture(scope="function")
def populate_db(db_session, author_validated_data_list, book_data_list):
    dates = (date(2024, month, 1) for month in range(1, 7))
    for author, book in zip(author_validated_data_list, book_data_list):
        with freeze_time(dates):
            author_obj = AuthorSQLCrud.create(db_session, author)
            book_validated_data = BookCreateValidator(**book)
            book_obj = BookSQLCrud.create(db_session, book_validated_data)
            book_obj.authors.append(author_obj)
            db_session.commit()
