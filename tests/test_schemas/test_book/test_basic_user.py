import pytest
from strawberry import Schema

from schema.basic import Query


@pytest.fixture(scope="function")
def test_schema(override_sqlalchemy_session):
    return Schema(query=Query, extensions=[override_sqlalchemy_session])


class TestBookList:
    @pytest.fixture(scope="function")
    def book_list_query(self):
        return """query {
            bookList {
                id
                title
                authors {
                    id
                    firstName
                    middleName
                    lastName
                }
                publicationYear
                language
                category
            }
        }"""

    @pytest.fixture(scope="function")
    def book_list_query_with_filter(self):
        return """query {
            bookList(f: {title: "dra"}) {
                id
                title
                authors {
                    id
                    firstName
                    middleName
                    lastName
                }
                publicationYear
                language
                category
            }
        }"""

    async def test_book_list_query_returns_correct_fields(
        self, populate_db, request_obj, test_schema, book_list_query
    ):
        result = await test_schema.execute(
            book_list_query, context_value={"request": request_obj}
        )
        assert not result.errors
        assert tuple(result.data["bookList"][0].keys()) == (
            "id",
            "title",
            "authors",
            "publicationYear",
            "language",
            "category",
        )
        assert tuple(result.data["bookList"][0]["authors"][0].keys()) == (
            "id",
            "firstName",
            "middleName",
            "lastName",
        )

    async def test_book_list_query_as_basic_user_without_filter(
        self, populate_db, request_obj, test_schema, book_list_query
    ):
        result = await test_schema.execute(
            book_list_query, context_value={"request": request_obj}
        )
        assert not result.errors
        assert len(result.data["bookList"]) == 3

    async def test_book_list_query_as_basic_user_with_filter(
        self, populate_db, request_obj, test_schema, book_list_query_with_filter
    ):
        result = await test_schema.execute(
            book_list_query_with_filter, context_value={"request": request_obj}
        )
        assert not result.errors
        assert len(result.data["bookList"]) == 1
        for author in result.data["bookList"]:
            assert "dra" in author["title"].lower()
