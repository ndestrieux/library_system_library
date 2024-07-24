import pytest
from strawberry import Schema

from database.validators.author import AuthorCreateValidator
from src.database.crud_factory import AuthorSQLCrud
from src.schema import Mutation, Query


@pytest.fixture(scope="function")
def test_schema(override_sqlalchemy_session):
    return Schema(
        query=Query, mutation=Mutation, extensions=[override_sqlalchemy_session]
    )


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


@pytest.fixture(scope="function")
def graphql_create_author_query():
    """Generate author data."""
    return """mutation {
      newAuthor(data: {firstName: "Dale", lastName: "Cooper"})  {
        id
        firstName
        lastName
      }
    }"""


@pytest.fixture(scope="function")
def graphql_update_author_query():
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
def graphql_update_author_query_wrong_id():
    """Generate author data."""
    return """mutation {
      modifyAuthor(authorId: 100, data: {firstName: "J.R.R.", middleName: null})  {
        id
        firstName
        middleName
        lastName
      }
    }"""


@pytest.fixture(scope="function")
def graphql_delete_author_query():
    return """mutation {
        removeAuthor(authorId: 1)
    }"""


@pytest.fixture(scope="function")
def graphql_delete_author_query_wrong_id():
    return """mutation {
        removeAuthor(authorId: 100)
    }"""


async def test_author_list_without_filter(populate_db, test_schema, author_list_query):
    result = await test_schema.execute(
        author_list_query, context_value={"requester": "user"}
    )
    assert not result.errors
    assert len(result.data["authorList"]) == 3


async def test_author_list_with_filter(
    populate_db, test_schema, author_list_query_with_filter
):
    result = await test_schema.execute(
        author_list_query_with_filter, context_value={"requester": "user"}
    )
    assert not result.errors
    assert len(result.data["authorList"]) == 2


async def test_author_details(populate_db, test_schema, author_details_query):
    result = await test_schema.execute(
        author_details_query, context_value={"requester": "user"}
    )
    assert not result.errors
    assert result.data["authorDetails"]["id"] == 1


async def test_author_details_when_entry_does_not_exist(
    populate_db, test_schema, author_details_query_wrong_id
):
    result = await test_schema.execute(
        author_details_query_wrong_id, context_value={"requester": "user"}
    )
    assert result.errors


async def test_author_creation(request_obj, graphql_create_author_query, test_schema):
    result = await test_schema.execute(
        graphql_create_author_query, context_value={"request": request_obj}
    )
    assert not result.errors
    assert result.data["newAuthor"] == {
        "id": 1,
        "firstName": "Dale",
        "lastName": "Cooper",
    }


async def test_author_update(
    populate_db, request_obj, graphql_update_author_query, test_schema
):
    result = await test_schema.execute(
        graphql_update_author_query, context_value={"request": request_obj}
    )
    assert not result.errors
    assert result.data["modifyAuthor"] == {
        "id": 3,
        "firstName": "J.R.R.",
        "middleName": None,
        "lastName": "Tolkien",
    }


async def test_author_update_when_entry_does_not_exist(
    populate_db, request_obj, graphql_update_author_query_wrong_id, test_schema
):
    result = await test_schema.execute(
        graphql_update_author_query_wrong_id, context_value={"request": request_obj}
    )
    assert result.errors


async def test_author_delete(
    populate_db, request_obj, graphql_delete_author_query, test_schema
):
    result = await test_schema.execute(
        graphql_delete_author_query, context_value={"request": request_obj}
    )
    assert result.data["removeAuthor"]


async def test_author_delete_when_entry_does_not_exist(
    populate_db, request_obj, graphql_delete_author_query_wrong_id, test_schema
):
    result = await test_schema.execute(
        graphql_delete_author_query_wrong_id, context_value={"request": request_obj}
    )
    assert not result.data["removeAuthor"]
