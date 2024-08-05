import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.requests import Request
from strawberry.extensions import SchemaExtension

from database.models import Base
from src.permissions import HasAdminGroup


def pytest_addoption(parser):
    parser.addoption(
        "--dburl",
        action="store",
        # default="sqlite:///./test_db.sqlite3",  # Default uses SQLite in memory db
        default="sqlite:///./library.sqlite3",
        help="Database URL to use for tests.",
    )


@pytest.fixture(scope="session")
def db_url(request):
    """Fixture to retrieve the database URL."""
    return request.config.getoption("--dburl")


@pytest.fixture(scope="function")
def engine(db_url):
    """Create engine for tests"""
    return create_engine(db_url)


@pytest.fixture(scope="function")
def tables(engine):
    """Create and then drop tables"""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(engine, tables):
    """Create DB session for tests, transactions are rolled back at the end"""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def override_sqlalchemy_session(db_session):
    """Create a test client that uses the override_get_db fixture to return a session"""

    class OverrideSQLAlchemySession(SchemaExtension):
        def on_operation(self):
            self.execution_context.context["db"] = db_session
            yield
            self.execution_context.context["db"].close()

    return OverrideSQLAlchemySession


@pytest.fixture(scope="session")
def request_headers():
    """Request headers for basic user"""
    return {
        "requester": "user",
    }


@pytest.fixture(scope="session")
def request_obj(request_headers):
    """Create request object coming from basic user"""
    request = Request(
        {
            "type": "http",
        }
    )
    request._headers = request_headers
    return request


@pytest.fixture(scope="session")
def admin_request_headers():
    """Request headers for admin user"""
    return {
        "requester": "admin",
        "groups": [
            "admin",
        ],
    }


@pytest.fixture(scope="session")
def admin_request_obj(admin_request_headers):
    """Create request object coming from admin user"""
    request = Request(
        {
            "type": "http",
        }
    )
    request._headers = admin_request_headers
    return request


@pytest.fixture(scope="session")
def no_admin_permission_error():
    return HasAdminGroup.message
