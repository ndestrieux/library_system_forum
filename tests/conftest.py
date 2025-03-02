from enum import StrEnum, auto
from typing import Generator

import pytest
from faker import Faker
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from database.models import BaseModel
from datastructures import RequesterData
from dependencies import get_db
from main import app
from routers import jwt_token


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--dburl",
        action="store",
        default="sqlite:///./test_forum.sqlite3",
        help="Database URL to use for tests.",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session) -> None:
    db_url = session.config.getoption("--dburl")
    try:
        engine = create_engine(
            db_url,
            poolclass=StaticPool,
        )
        connection = engine.connect()
        connection.close()
        print("Database connection successful........")
    except SQLAlchemyOperationalError as e:
        print(f"Failed to connect to the database at {db_url}: {e}")
        pytest.exit(
            "Stopping tests because database connection could not be established."
        )


@pytest.fixture(scope="class")
def db_url(request) -> str:
    """Fixture to retrieve the database URL."""
    return request.config.getoption("--dburl")


@pytest.fixture(scope="class")
def db_session(db_url) -> Generator[Session, None, None]:
    """Create a new database session with a rollback at the end of the test."""
    engine = create_engine(
        db_url,
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    BaseModel.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def async_test_client(db_session) -> Generator[AsyncClient, None, None]:
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost/api/forum"
    )


class Users(StrEnum):
    TEST_BASIC_USER = auto()
    TEST_ANOTHER_BASIC_USER = auto()
    TEST_MODERATOR = auto()
    TEST_ANOTHER_MODERATOR = auto()


USER_GROUPS = {
    Users.TEST_BASIC_USER: ["basic"],
    Users.TEST_ANOTHER_BASIC_USER: ["basic"],
    Users.TEST_MODERATOR: ["moderator"],
    Users.TEST_ANOTHER_MODERATOR: ["moderator"],
}


@pytest.fixture
def override_jwt_token(request) -> None:
    user_name = request.param

    def jwt_token_decode() -> Generator[RequesterData, None, None]:
        yield RequesterData(name=user_name, groups=USER_GROUPS[user_name])

    app.dependency_overrides[jwt_token.decode] = jwt_token_decode
    yield
    del app.dependency_overrides[jwt_token.decode]


@pytest.fixture(scope="session")
def get_faker():
    return Faker()
