import pytest
from strawberry import Schema

from src.schema.admin import Mutation, Query


@pytest.fixture(scope="function")
def test_schema(override_sqlalchemy_session):
    return Schema(
        query=Query, mutation=Mutation, extensions=[override_sqlalchemy_session]
    )


@pytest.fixture(scope="function")
def author_list_query():
    return """query {
        authorList {
            firstName
            lastName
        }
    }"""


@pytest.fixture(scope="function")
def author_list_query_with_filter():
    return """query {
        authorList(f: {lastName: "co"}) {
            firstName
            lastName
        }
    }"""


@pytest.fixture(scope="function")
def author_details_query():
    return """
        query {
            authorDetails(authorId: 1)  {
            id
            lastName
        }
    }"""


@pytest.fixture(scope="function")
def author_details_query_wrong_id():
    return """
        query {
            authorDetails(authorId: 100)  {
            id
            lastName
        }
    }"""


class TestAuthorCreation:
    @pytest.fixture(scope="function")
    def graphql_create_author_query(self):
        """Generate author data."""
        return """mutation {
          newAuthor(data: {firstName: "Dale", lastName: "Cooper"})  {
            id
            firstName
            lastName
          }
        }"""

    async def test_author_creation(
        self, admin_request_obj, graphql_create_author_query, test_schema
    ):
        result = await test_schema.execute(
            graphql_create_author_query, context_value={"request": admin_request_obj}
        )
        assert not result.errors
        assert result.data["newAuthor"] == {
            "id": 1,
            "firstName": "Dale",
            "lastName": "Cooper",
        }


class TestAuthorUpdate:
    @pytest.fixture(scope="function")
    def graphql_update_author_query(self):
        """Generate author data."""
        return """mutation {
          modifyAuthor(authorId: 3, data: {firstName: "J.R.R.", middleName: null})  {
            id
            firstName
            middleName
            lastName
          }
        }"""

    @pytest.fixture(scope="function")
    def graphql_update_author_query_wrong_id(self):
        """Generate author data."""
        return """mutation {
          modifyAuthor(authorId: 100, data: {firstName: "J.R.R.", middleName: null})  {
            id
            firstName
            middleName
            lastName
          }
        }"""

    async def test_author_update(
        self, populate_db, admin_request_obj, graphql_update_author_query, test_schema
    ):
        result = await test_schema.execute(
            graphql_update_author_query, context_value={"request": admin_request_obj}
        )
        assert not result.errors
        assert result.data["modifyAuthor"] == {
            "id": 3,
            "firstName": "J.R.R.",
            "middleName": None,
            "lastName": "Tolkien",
        }

    async def test_author_update_when_entry_does_not_exist(
        self,
        populate_db,
        admin_request_obj,
        graphql_update_author_query_wrong_id,
        test_schema,
    ):
        result = await test_schema.execute(
            graphql_update_author_query_wrong_id,
            context_value={"request": admin_request_obj},
        )
        assert result.errors


class TestAuthorDelete:
    @pytest.fixture(scope="function")
    def graphql_delete_author_query(self):
        return """mutation {
            removeAuthor(authorId: 1)
        }"""

    @pytest.fixture(scope="function")
    def graphql_delete_author_query_wrong_id(self):
        return """mutation {
            removeAuthor(authorId: 100)
        }"""

    async def test_author_delete(
        self, populate_db, admin_request_obj, graphql_delete_author_query, test_schema
    ):
        result = await test_schema.execute(
            graphql_delete_author_query, context_value={"request": admin_request_obj}
        )
        assert result.data["removeAuthor"]

    async def test_author_delete_when_entry_does_not_exist(
        self,
        populate_db,
        admin_request_obj,
        graphql_delete_author_query_wrong_id,
        test_schema,
    ):
        result = await test_schema.execute(
            graphql_delete_author_query_wrong_id,
            context_value={"request": admin_request_obj},
        )
        assert not result.data["removeAuthor"]
