from datetime import date

import pytest
from freezegun import freeze_time
from strawberry import Schema

from src.schema.admin import Mutation, Query


@pytest.fixture(scope="function")
def test_schema(override_sqlalchemy_session):
    return Schema(
        query=Query, mutation=Mutation, extensions=[override_sqlalchemy_session]
    )


class TestAuthorListAdmin:
    @pytest.fixture(scope="function")
    def author_list_admin_query(self):
        return """query {
            authorListAdmin {
                id
                firstName
                middleName
                lastName
                createdBy
                createdOn
                lastUpdatedBy
                lastUpdatedOn
            }
        }"""

    @pytest.fixture(scope="function")
    def author_list_admin_query_with_filter(self):
        return """query {
            authorListAdmin(f: {lastName: "co"}) {
                id
                firstName
                middleName
                lastName
                createdBy
                createdOn
                lastUpdatedBy
                lastUpdatedOn
            }
        }"""

    @pytest.fixture(scope="function")
    def author_list_admin_query_with_filter_on_creation_date(self):
        return """query {
            authorListAdmin(f: {createdBetween: {from_: "2024-01-15", to_: "2024-02-15"}}) {
                id
                firstName
                middleName
                lastName
                createdBy
                createdOn
                lastUpdatedBy
                lastUpdatedOn
            }
        }"""

    async def test_author_list_admin_query_returns_correct_fields(
        self, populate_db, admin_request_obj, test_schema, author_list_admin_query
    ):
        result = await test_schema.execute(
            author_list_admin_query, context_value={"request": admin_request_obj}
        )
        assert not result.errors
        assert tuple(result.data["authorListAdmin"][0].keys()) == (
            "id",
            "firstName",
            "middleName",
            "lastName",
            "createdBy",
            "createdOn",
            "lastUpdatedBy",
            "lastUpdatedOn",
        )

    async def test_author_list_admin_query_as_admin_user_without_filter(
        self, populate_db, admin_request_obj, test_schema, author_list_admin_query
    ):
        result = await test_schema.execute(
            author_list_admin_query, context_value={"request": admin_request_obj}
        )
        assert not result.errors
        assert len(result.data["authorListAdmin"]) == 3

    async def test_author_list_admin_query_as_admin_user_with_filter(
        self,
        populate_db,
        admin_request_obj,
        test_schema,
        author_list_admin_query_with_filter,
    ):
        result = await test_schema.execute(
            author_list_admin_query_with_filter,
            context_value={"request": admin_request_obj},
        )
        assert not result.errors
        assert len(result.data["authorListAdmin"]) == 2
        for author in result.data["authorListAdmin"]:
            assert "co" in author["lastName"].lower()

    async def test_author_list_admin_query_as_admin_user_with_creation_date_filter(
        self,
        populate_db,
        admin_request_obj,
        test_schema,
        author_list_admin_query_with_filter_on_creation_date,
    ):
        result = await test_schema.execute(
            author_list_admin_query_with_filter_on_creation_date,
            context_value={"request": admin_request_obj},
        )
        assert not result.errors
        assert len(result.data["authorListAdmin"]) == 1
        assert (
            "2024-01-15"
            <= result.data["authorListAdmin"][0]["createdOn"]
            <= "2024-02-15"
        )

    async def test_author_list_admin_query_as_basic_user_throws_error(
        self,
        request_obj,
        test_schema,
        author_list_admin_query,
        no_admin_permission_error,
    ):
        result = await test_schema.execute(
            author_list_admin_query, context_value={"request": request_obj}
        )
        assert result.errors
        assert result.errors[0].message == no_admin_permission_error


class TestAuthorDetails:
    @pytest.fixture(scope="function")
    def author_details_admin_query(self):
        return """
            query {
                authorDetailsAdmin(authorId: 1)  {
                id
                firstName
                middleName
                lastName
                createdBy
                createdOn
                lastUpdatedBy
                lastUpdatedOn
            }
        }"""

    @pytest.fixture(scope="function")
    def author_details_admin_query_wrong_id(self):
        return """
            query {
                authorDetailsAdmin(authorId: 100)  {
                id
                firstName
                middleName
                lastName
                createdBy
                createdOn
                lastUpdatedBy
                lastUpdatedOn
            }
        }"""

    async def test_author_details_admin_query_returns_correct_fields(
        self, populate_db, admin_request_obj, test_schema, author_details_admin_query
    ):
        result = await test_schema.execute(
            author_details_admin_query, context_value={"request": admin_request_obj}
        )
        assert not result.errors
        assert tuple(result.data["authorDetailsAdmin"].keys()) == (
            "id",
            "firstName",
            "middleName",
            "lastName",
            "createdBy",
            "createdOn",
            "lastUpdatedBy",
            "lastUpdatedOn",
        )

    async def test_author_details_query_as_admin_user(
        self, populate_db, admin_request_obj, test_schema, author_details_admin_query
    ):
        result = await test_schema.execute(
            author_details_admin_query, context_value={"request": admin_request_obj}
        )
        assert not result.errors
        assert result.data["authorDetailsAdmin"]["id"] == 1

    async def test_author_details_as_admin_user_when_author_id_does_not_exist(
        self,
        populate_db,
        admin_request_obj,
        test_schema,
        author_details_admin_query_wrong_id,
    ):
        result = await test_schema.execute(
            author_details_admin_query_wrong_id,
            context_value={"request": admin_request_obj},
        )
        assert result.errors

    async def test_author_details_admin_query_as_basic_user_throws_error(
        self,
        request_obj,
        test_schema,
        author_details_admin_query,
        no_admin_permission_error,
    ):
        result = await test_schema.execute(
            author_details_admin_query, context_value={"request": request_obj}
        )
        assert result.errors
        assert result.errors[0].message == no_admin_permission_error


class TestAuthorCreation:
    @pytest.fixture(scope="function")
    def graphql_create_author_mutation(self):
        """Generate author data."""
        return """mutation {
          newAuthor(data: {firstName: "Dale", lastName: "Cooper"})  {
                id
                firstName
                middleName
                lastName
                createdBy
                createdOn
                lastUpdatedBy
                lastUpdatedOn
          }
        }"""

    async def test_create_author_mutation(
        self, admin_request_obj, graphql_create_author_query, test_schema
    ):
        with freeze_time(date(2024, 4, 1)):
            result = await test_schema.execute(
                graphql_create_author_query,
                context_value={"request": admin_request_obj},
            )
        assert not result.errors
        assert result.data["newAuthor"] == {
            "id": 1,
            "firstName": "Dale",
            "middleName": None,
            "lastName": "Cooper",
            "createdBy": "admin",
            "createdOn": "2024-04-01",
            "lastUpdatedBy": None,
            "lastUpdatedOn": None,
        }

    async def test_create_author_mutation_as_basic_user_throws_error(
        self,
        request_obj,
        test_schema,
        graphql_create_author_query,
        no_admin_permission_error,
    ):
        result = await test_schema.execute(
            graphql_create_author_query, context_value={"request": request_obj}
        )
        assert result.errors
        assert result.errors[0].message == no_admin_permission_error


class TestAuthorUpdate:
    @pytest.fixture(scope="function")
    def graphql_update_author_mutation(self):
        """Generate author data."""
        return """mutation {
          modifyAuthor(authorId: 3, data: {firstName: "J.R.R.", middleName: null})  {
                id
                firstName
                middleName
                lastName
                createdBy
                createdOn
                lastUpdatedBy
                lastUpdatedOn
          }
        }"""

    @pytest.fixture(scope="function")
    def graphql_update_author_mutation_wrong_id(self):
        """Generate author data."""
        return """mutation {
          modifyAuthor(authorId: 100, data: {firstName: "J.R.R.", middleName: null})  {
                id
          }
        }"""

    async def test_author_update_mutation(
        self,
        populate_db,
        admin_request_obj,
        graphql_update_author_mutation,
        test_schema,
    ):
        with freeze_time(date(2024, 5, 1)):
            result = await test_schema.execute(
                graphql_update_author_mutation,
                context_value={"request": admin_request_obj},
            )
        assert not result.errors
        assert result.data["modifyAuthor"] == {
            "id": 3,
            "firstName": "J.R.R.",
            "middleName": None,
            "lastName": "Tolkien",
            "createdBy": "admin",
            "createdOn": "2024-03-01",
            "lastUpdatedBy": "admin",
            "lastUpdatedOn": "2024-05-01",
        }

    async def test_update_author_mutation_when_author_id_does_not_exist(
        self,
        populate_db,
        admin_request_obj,
        graphql_update_author_mutation_wrong_id,
        test_schema,
    ):
        result = await test_schema.execute(
            graphql_update_author_mutation_wrong_id,
            context_value={"request": admin_request_obj},
        )
        assert result.errors

    async def test_update_author_mutation_as_basic_user_throws_error(
        self,
        request_obj,
        test_schema,
        graphql_update_author_mutation,
        no_admin_permission_error,
    ):
        result = await test_schema.execute(
            graphql_update_author_mutation, context_value={"request": request_obj}
        )
        assert result.errors
        assert result.errors[0].message == no_admin_permission_error


class TestAuthorDelete:
    @pytest.fixture(scope="function")
    def graphql_delete_author_mutation(self):
        return """mutation {
            removeAuthor(authorId: 1)
        }"""

    @pytest.fixture(scope="function")
    def graphql_delete_author_mutation_wrong_id(self):
        return """mutation {
            removeAuthor(authorId: 100)
        }"""

    async def test_delete_author_mutation(
        self, populate_db, admin_request_obj, graphql_delete_author_query, test_schema
    ):
        result = await test_schema.execute(
            graphql_delete_author_query, context_value={"request": admin_request_obj}
        )
        assert result.data["removeAuthor"]

    async def test_delete_author_mutation_when_author_id_does_not_exist(
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

    async def test_author_delete_admin_mutation_as_basic_user_throws_error(
        self,
        request_obj,
        test_schema,
        graphql_delete_author_query,
        no_admin_permission_error,
    ):
        result = await test_schema.execute(
            graphql_delete_author_query, context_value={"request": request_obj}
        )
        assert result.errors
        assert result.errors[0].message == no_admin_permission_error
