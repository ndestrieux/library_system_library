from datetime import date

import pytest
from freezegun import freeze_time
from strawberry import Schema

from database.crud_factory import AuthorSQLCrud, BookSQLCrud
from filters.book import BookAdminFilter
from schema.admin import Mutation, Query


@pytest.fixture(scope="function")
def test_schema(override_sqlalchemy_session):
    return Schema(
        query=Query, mutation=Mutation, extensions=[override_sqlalchemy_session]
    )


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


class TestBookCreation:
    @pytest.fixture(scope="function")
    def graphql_create_book_mutation(self):
        """Generate book data."""
        return """mutation {
          newBook(data:
          {title: "The Silmarillion", publicationYear: 1977, language: "English", category: "Fantasy", authors: [3]}
          )  {
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
    def graphql_create_book_mutation_without_related_author_id(self):
        """Generate book data."""
        return """mutation {
          newBook(data:
          {title: "New book", publicationYear: 2000, language: "English", category: "Fantasy", authors: []}
          )  {
                id
          }
        }"""

    @pytest.fixture(scope="function")
    def graphql_create_book_mutation_with_a_related_author_id_that_does_not_exist(self):
        """Generate book data."""
        return """mutation {
          newBook(data:
          {title: "New book", publicationYear: 2000, language: "English", category: "Fantasy", authors: [1, 100]}
          )  {
                id
          }
        }"""

    async def test_create_book_mutation(
        self, populate_db, admin_request_obj, graphql_create_book_mutation, test_schema
    ):
        with freeze_time(date(2024, 4, 1)):
            result = await test_schema.execute(
                graphql_create_book_mutation,
                context_value={"request": admin_request_obj},
            )
        assert not result.errors
        assert result.data["newBook"] == {
            "id": 4,
            "title": "The Silmarillion",
            "authors": [
                {
                    "id": 3,
                    "firstName": "John",
                    "middleName": "Ronald Reuel",
                    "lastName": "Tolkien",
                }
            ],
            "publicationYear": 1977,
            "language": "LanguageChoices.EN",
            "category": "Fantasy",
            "createdBy": "admin",
            "createdOn": "2024-04-01",
            "lastUpdatedBy": None,
            "lastUpdatedOn": None,
        }

    async def test_create_book_mutation_without_related_author_id(
        self,
        populate_db,
        admin_request_obj,
        graphql_create_book_mutation_without_related_author_id,
        test_schema,
        db_session,
    ):
        with freeze_time(date(2024, 4, 1)):
            result = await test_schema.execute(
                graphql_create_book_mutation_without_related_author_id,
                context_value={"request": admin_request_obj},
            )
        assert result.errors
        assert "validation error" in result.errors[0].message
        q_filter = BookAdminFilter(title="New book")
        assert not list(BookSQLCrud.get_many_by_values(db_session, q_filter=q_filter))

    async def test_create_book_mutation_with_related_author_id_that_does_not_exist(
        self,
        populate_db,
        admin_request_obj,
        graphql_create_book_mutation_with_a_related_author_id_that_does_not_exist,
        test_schema,
        db_session,
    ):
        with freeze_time(date(2024, 4, 1)):
            result = await test_schema.execute(
                graphql_create_book_mutation_with_a_related_author_id_that_does_not_exist,
                context_value={"request": admin_request_obj},
            )
        assert result.errors
        assert (
            result.errors[0].message
            == "Author object with id '100' could not be found."
        )

    async def test_create_book_mutation_as_basic_user_throws_error(
        self,
        request_obj,
        test_schema,
        graphql_create_book_mutation,
        no_admin_permission_error,
    ):
        result = await test_schema.execute(
            graphql_create_book_mutation, context_value={"request": request_obj}
        )
        assert result.errors
        assert result.errors[0].message == no_admin_permission_error


class TestBookUpdate:
    @pytest.fixture(scope="function")
    def graphql_update_book_mutation(self):
        """Generate book data."""
        return """mutation {
          modifyBook(bookId: 3, data: {title: "The Hobbit Remastered"})  {
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
    def graphql_update_book_mutation_add_author(self):
        """Generate book data."""
        return """mutation {
          modifyBook(bookId: 1, data: {addAuthors: [3]})  {
                id
          }
        }"""

    @pytest.fixture(scope="function")
    def graphql_update_book_mutation_add_author_remove_another(self):
        """Generate book data."""
        return """mutation {
          modifyBook(bookId: 1, data: {addAuthors: [3], removeAuthors: [1]})  {
                id
          }
        }"""

    @pytest.fixture(scope="function")
    def graphql_update_book_mutation_remove_unique_author(self):
        """Generate book data."""
        return """mutation {
          modifyBook(bookId: 1, data: {removeAuthors: [1]})  {
                id
          }
        }"""

    @pytest.fixture(scope="function")
    def graphql_update_book_mutation_remove_author_that_does_not_exist(self):
        """Generate book data."""
        return """mutation {
          modifyBook(bookId: 1, data: {addAuthors: [3], removeAuthors: [100]})  {
                id
          }
        }"""

    @pytest.fixture(scope="function")
    def graphql_update_book_mutation_remove_author_that_is_not_related_to_book_object(
        self,
    ):
        """Generate book data."""
        return """mutation {
          modifyBook(bookId: 1, data: {addAuthors: [3], removeAuthors: [2]})  {
                id
          }
        }"""

    @pytest.fixture(scope="function")
    def graphql_update_book_mutation_wrong_id(self):
        """Generate book data."""
        return """mutation {
          modifyBook(bookId: 100, data: {title: "The Hobbit Remastered"})  {
                id
          }
        }"""

    async def test_book_update_mutation(
        self,
        populate_db,
        admin_request_obj,
        graphql_update_book_mutation,
        test_schema,
    ):
        with freeze_time(date(2024, 5, 1)):
            result = await test_schema.execute(
                graphql_update_book_mutation,
                context_value={"request": admin_request_obj},
            )
        assert not result.errors
        assert result.data["modifyBook"] == {
            "id": 3,
            "title": "The Hobbit Remastered",
            "authors": [
                {
                    "id": 3,
                    "firstName": "John",
                    "middleName": "Ronald Reuel",
                    "lastName": "Tolkien",
                }
            ],
            "publicationYear": 1937,
            "language": "LanguageChoices.EN",
            "category": "Fantasy",
            "createdBy": "admin",
            "createdOn": "2024-03-01",
            "lastUpdatedBy": "admin",
            "lastUpdatedOn": "2024-05-01",
        }

    async def test_update_book_mutation_when_book_id_does_not_exist(
        self,
        populate_db,
        admin_request_obj,
        graphql_update_book_mutation_wrong_id,
        test_schema,
    ):
        result = await test_schema.execute(
            graphql_update_book_mutation_wrong_id,
            context_value={"request": admin_request_obj},
        )
        assert result.errors

    async def test_update_book_mutation_when_adding_author(
        self,
        populate_db,
        admin_request_obj,
        graphql_update_book_mutation_add_author,
        test_schema,
        db_session,
    ):
        result = await test_schema.execute(
            graphql_update_book_mutation_add_author,
            context_value={"request": admin_request_obj},
        )
        assert not result.errors
        author_obj = AuthorSQLCrud.get_one_by_id(db_session, 3)
        book_authors = BookSQLCrud.get_one_by_id(db_session, 1).authors
        assert author_obj in book_authors

    async def test_update_book_mutation_when_removing_author_and_there_is_more_than_one_remaining_author(
        self,
        populate_db,
        admin_request_obj,
        graphql_update_book_mutation_add_author_remove_another,
        test_schema,
        db_session,
    ):
        result = await test_schema.execute(
            graphql_update_book_mutation_add_author_remove_another,
            context_value={"request": admin_request_obj},
        )
        assert not result.errors
        assert len(BookSQLCrud.get_one_by_id(db_session, 1).authors) > 0

    async def test_update_book_mutation_when_removing_the_sole_related_author(
        self,
        populate_db,
        admin_request_obj,
        graphql_update_book_mutation_remove_unique_author,
        test_schema,
    ):
        result = await test_schema.execute(
            graphql_update_book_mutation_remove_unique_author,
            context_value={"request": admin_request_obj},
        )
        assert result.errors

    async def test_update_book_mutation_when_removing_author_that_does_not_exist(
        self,
        populate_db,
        admin_request_obj,
        graphql_update_book_mutation_remove_author_that_does_not_exist,
        test_schema,
    ):
        result = await test_schema.execute(
            graphql_update_book_mutation_remove_author_that_does_not_exist,
            context_value={"request": admin_request_obj},
        )
        assert not result.errors

    async def test_update_book_mutation_when_removing_author_that_is_not_related_to_book_object(
        self,
        populate_db,
        admin_request_obj,
        graphql_update_book_mutation_remove_author_that_is_not_related_to_book_object,
        test_schema,
    ):
        result = await test_schema.execute(
            graphql_update_book_mutation_remove_author_that_is_not_related_to_book_object,
            context_value={"request": admin_request_obj},
        )
        assert not result.errors

    async def test_update_book_mutation_as_basic_user_throws_error(
        self,
        request_obj,
        test_schema,
        graphql_update_book_mutation,
        no_admin_permission_error,
    ):
        result = await test_schema.execute(
            graphql_update_book_mutation, context_value={"request": request_obj}
        )
        assert result.errors
        assert result.errors[0].message == no_admin_permission_error


class TestAuthorDelete:
    @pytest.fixture(scope="function")
    def graphql_delete_book_mutation(self):
        return """mutation {
            removeBook(bookId: 1)
        }"""

    @pytest.fixture(scope="function")
    def graphql_delete_book_mutation_wrong_id(self):
        return """mutation {
            removeBook(bookId: 100)
        }"""

    async def test_delete_book_mutation(
        self,
        populate_db,
        admin_request_obj,
        graphql_delete_book_mutation,
        test_schema,
    ):
        result = await test_schema.execute(
            graphql_delete_book_mutation, context_value={"request": admin_request_obj}
        )
        assert result.data["removeBook"]

    async def test_delete_book_mutation_when_book_id_does_not_exist(
        self,
        populate_db,
        admin_request_obj,
        graphql_delete_book_mutation_wrong_id,
        test_schema,
    ):
        result = await test_schema.execute(
            graphql_delete_book_mutation_wrong_id,
            context_value={"request": admin_request_obj},
        )
        assert not result.data["removeBook"]

    async def test_book_delete_admin_mutation_as_basic_user_throws_error(
        self,
        request_obj,
        test_schema,
        graphql_delete_book_mutation,
        no_admin_permission_error,
    ):
        result = await test_schema.execute(
            graphql_delete_book_mutation, context_value={"request": request_obj}
        )
        assert result.errors
        assert result.errors[0].message == no_admin_permission_error
