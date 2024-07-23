import pytest
from strawberry import Schema

from database.models import Author as AuthorModel
from database.validators.author import AuthorCreateValidator
from src.database.crud_factory import crud_factory
from src.schema import Mutation, Query


@pytest.fixture(scope="function")
def test_schema(override_sqlalchemy_session):
    return Schema(
        query=Query, mutation=Mutation, extensions=[override_sqlalchemy_session]
    )


@pytest.fixture(scope="module")
def author_crud():
    return crud_factory(AuthorModel)


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
def populate_db(db_session, author_crud, author_validated_data_list):
    for author in author_validated_data_list:
        author_crud.create(db_session, author)


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
def graphql_create_author_query():
    """Generate author data."""
    return """mutation {
      newAuthor(data: {firstName: "Dale", lastName: "Cooper"})  {
        id
        firstName
        lastName
      }
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
