import pytest
from strawberry import Schema

from schema.admin import Query


@pytest.fixture(scope="function")
def test_schema(override_sqlalchemy_session):
    return Schema(query=Query, extensions=[override_sqlalchemy_session])


class TestBookListAdmin:
    @pytest.fixture(scope="function")
    def book_list_admin_query(self):
        return """query {
            bookListAdmin {
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
                createdBy
                createdOn
                lastUpdatedBy
                lastUpdatedOn
            }
        }"""

    @pytest.fixture(scope="function")
    def book_list_admin_query_with_filter(self):
        return """query {
            bookListAdmin(f: {title: "dra"}) {
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
                createdBy
                createdOn
                lastUpdatedBy
                lastUpdatedOn
            }
        }"""

    @pytest.fixture(scope="function")
    def book_list_admin_query_with_filter_on_creation_date(self):
        return """query {
            bookListAdmin(f: {createdBetween: {from_: "2024-01-15", to_: "2024-02-15"}}) {
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
                createdBy
                createdOn
                lastUpdatedBy
                lastUpdatedOn
            }
        }"""

    async def test_book_list_admin_query_as_admin_user_returns_correct_fields(
        self, populate_db, request_obj, test_schema, book_list_admin_query
    ):
        result = await test_schema.execute(
            book_list_admin_query, context_value={"request": request_obj}
        )
        assert not result.errors
        assert tuple(result.data["bookListAdmin"][0].keys()) == (
            "id",
            "title",
            "authors",
            "publicationYear",
            "language",
            "category",
            "createdBy",
            "createdOn",
            "lastUpdatedBy",
            "lastUpdatedOn",
        )
        assert tuple(result.data["bookListAdmin"][0]["authors"][0].keys()) == (
            "id",
            "firstName",
            "middleName",
            "lastName",
        )

    async def test_book_list_admin_query_as_admin_user_without_filter(
        self, populate_db, request_obj, test_schema, book_list_admin_query
    ):
        result = await test_schema.execute(
            book_list_admin_query, context_value={"request": request_obj}
        )
        assert not result.errors
        assert len(result.data["bookListAdmin"]) == 3

    async def test_book_list_admin_query_as_admin_user_with_filter(
        self, populate_db, request_obj, test_schema, book_list_admin_query_with_filter
    ):
        result = await test_schema.execute(
            book_list_admin_query_with_filter, context_value={"request": request_obj}
        )
        assert not result.errors
        assert len(result.data["bookListAdmin"]) == 1
        for author in result.data["bookListAdmin"]:
            assert "dra" in author["title"].lower()

    async def test_book_list_admin_query_as_admin_user_with_creation_date_filter(
        self,
        populate_db,
        admin_request_obj,
        test_schema,
        book_list_admin_query_with_filter_on_creation_date,
    ):
        result = await test_schema.execute(
            book_list_admin_query_with_filter_on_creation_date,
            context_value={"request": admin_request_obj},
        )
        assert not result.errors
        assert len(result.data["bookListAdmin"]) == 1
        assert (
            "2024-01-15" <= result.data["bookListAdmin"][0]["createdOn"] <= "2024-02-15"
        )


class TestBookDetailsAdmin:
    @pytest.fixture(scope="function")
    def book_details_admin_query(self):
        return """
            query {
                bookDetailsAdmin(bookId: 1)  {
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
                createdBy
                createdOn
                lastUpdatedBy
                lastUpdatedOn
            }
        }"""

    @pytest.fixture(scope="function")
    def book_details_admin_query_wrong_id(self):
        return """
            query {
                bookDetailsAdmin(authorId: 100)  {
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
                createdBy
                createdOn
                lastUpdatedBy
                lastUpdatedOn
            }
        }"""

    async def test_book_details_query_as_admin_user_returns_correct_fields(
        self, populate_db, request_obj, test_schema, book_details_admin_query
    ):
        result = await test_schema.execute(
            book_details_admin_query, context_value={"request": request_obj}
        )
        assert not result.errors
        assert tuple(result.data["bookDetailsAdmin"].keys()) == (
            "id",
            "title",
            "authors",
            "publicationYear",
            "language",
            "category",
            "createdBy",
            "createdOn",
            "lastUpdatedBy",
            "lastUpdatedOn",
        )
        assert tuple(result.data["bookDetailsAdmin"]["authors"][0].keys()) == (
            "id",
            "firstName",
            "middleName",
            "lastName",
        )

    async def test_book_details_query_as_admin_user(
        self, populate_db, request_obj, test_schema, book_details_admin_query
    ):
        result = await test_schema.execute(
            book_details_admin_query, context_value={"request": request_obj}
        )
        assert not result.errors
        assert result.data["bookDetailsAdmin"]["id"] == 1

    async def test_book_details_as_admin_user_when_entry_does_not_exist(
        self, populate_db, request_obj, test_schema, book_details_admin_query_wrong_id
    ):
        result = await test_schema.execute(
            book_details_admin_query_wrong_id, context_value={"request": request_obj}
        )
        assert result.errors
