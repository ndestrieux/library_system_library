import pytest
from strawberry import Schema

from src.schema import Mutation, Query


@pytest.fixture(scope="function")
def graphql_create_author_query():
    """Generate author data."""
    return """mutation {
      newAuthor(data: {firstName: "Dale", lastName: "Cooper"})  {
        id
        firstName
        middleName
        lastName
      }
    }"""


async def test_author_creation(request_obj, graphql_create_author_query, override_db):
    test_schema = Schema(query=Query, mutation=Mutation, extensions=[override_db])
    result = await test_schema.execute(
        graphql_create_author_query, context_value={"request": request_obj}
    )
    assert not result.errors
    assert result.data["newAuthor"] == {
        "id": 1,
        "firstName": "Dale",
        "middleName": None,
        "lastName": "Cooper",
    }
