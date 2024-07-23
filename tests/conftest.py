import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.requests import Request
from strawberry.extensions import SchemaExtension

from src.database.db_conf import Base


def pytest_addoption(parser):
    parser.addoption(
        "--dburl",  # For Postgres use "postgresql://user:password@localhost/dbname"
        action="store",
        default="sqlite:///./test_db.sqlite3",  # Default uses SQLite in memory db
        help="Database URL to use for tests.",
    )


@pytest.fixture(scope="session")
def db_url(request):
    """Fixture to retrieve the database URL."""
    return request.config.getoption("--dburl")


@pytest.fixture(scope="function")
def db_session(db_url):
    """Create a new database session with a rollback at the end of the test."""
    # Create a SQLAlchemy engine
    engine = create_engine(
        db_url,
        poolclass=StaticPool,
    )

    # Create a sessionmaker to manage sessions
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables in the database
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def override_sqlalchemy_session(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    class OverrideSQLAlchemySession(SchemaExtension):
        def on_operation(self):
            self.execution_context.context["db"] = db_session
            yield
            self.execution_context.context["db"].close()

    return OverrideSQLAlchemySession


@pytest.fixture(scope="function")
def request_headers():
    return {
        "requester": "user",
    }


@pytest.fixture(scope="function")
def request_obj(request_headers):
    request = Request(
        {
            "type": "http",
        }
    )
    request._headers = request_headers
    return request
