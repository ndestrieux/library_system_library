import pytest
from strawberry import Schema

from src.schema.basic import Query


@pytest.fixture(scope="function")
def test_schema(override_sqlalchemy_session):
    return Schema(query=Query, extensions=[override_sqlalchemy_session])


class TestAuthorList:
    @pytest.fixture(scope="function")
    def author_list_query(self):
        return """query {
            authorList {
                id
                firstName
                middleName
                lastName
            }
        }"""

    @pytest.fixture(scope="function")
    def author_list_query_with_filter(self):
        return """query {
            authorList(f: {lastName: "co"}) {
                id
                firstName
                middleName
                lastName
            }
        }"""

    async def test_author_list_query_returns_correct_fields(
        self, populate_db, request_obj, test_schema, author_list_query
    ):
        result = await test_schema.execute(
            author_list_query, context_value={"request": request_obj}
        )
        assert not result.errors
        assert tuple(result.data["authorList"][0].keys()) == (
            "id",
            "firstName",
            "middleName",
            "lastName",
        )

    async def test_author_list_query_as_basic_user_without_filter(
        self, populate_db, request_obj, test_schema, author_list_query
    ):
        result = await test_schema.execute(
            author_list_query, context_value={"request": request_obj}
        )
        assert not result.errors
        assert len(result.data["authorList"]) == 3

    async def test_author_list_query_as_basic_user_with_filter(
        self, populate_db, request_obj, test_schema, author_list_query_with_filter
    ):
        result = await test_schema.execute(
            author_list_query_with_filter, context_value={"request": request_obj}
        )
        assert not result.errors
        assert len(result.data["authorList"]) == 2
        for author in result.data["authorList"]:
            assert "co" in author["lastName"].lower()


class TestAuthorDetails:
    @pytest.fixture(scope="function")
    def author_details_query(self):
        return """
            query {
                authorDetails(authorId: 1)  {
                id
                firstName
                middleName
                lastName
            }
        }"""

    @pytest.fixture(scope="function")
    def author_details_query_wrong_id(self):
        return """
            query {
                authorDetails(authorId: 100)  {
                id
                firstName
                middleName
                lastName
            }
        }"""

    async def test_author_details_query_returns_correct_fields(
        self, populate_db, request_obj, test_schema, author_details_query
    ):
        result = await test_schema.execute(
            author_details_query, context_value={"request": request_obj}
        )
        assert not result.errors
        assert tuple(result.data["authorDetails"].keys()) == (
            "id",
            "firstName",
            "middleName",
            "lastName",
        )

    async def test_author_details_query_as_basic_user(
        self, populate_db, request_obj, test_schema, author_details_query
    ):
        result = await test_schema.execute(
            author_details_query, context_value={"request": request_obj}
        )
        assert not result.errors
        assert result.data["authorDetails"]["id"] == 1

    async def test_author_details_as_basic_user_when_entry_does_not_exist(
        self, populate_db, request_obj, test_schema, author_details_query_wrong_id
    ):
        result = await test_schema.execute(
            author_details_query_wrong_id, context_value={"request": request_obj}
        )
        assert result.errors
