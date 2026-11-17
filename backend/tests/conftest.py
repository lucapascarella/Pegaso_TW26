import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app import app
from modules.database import get_session
from modules.models.user import UserRole, UserSql
from modules.security import hash_password

PASSWORD = "Test-Password-123"


@pytest.fixture(name="session")
def session_fixture():
    """In-memory SQLite database, recreated for every test."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    from modules.models import device, user  # noqa: F401  (register the tables)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Test client whose endpoints use the in-memory session."""
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


def _headers_for(client, session, role: UserRole) -> dict:
    """Create a user with the given role, log in and return the Authorization header."""
    email = f"{role.value}@test.example"
    session.add(UserSql(email=email, full_name=role.value, role=role, hashed_password=hash_password(PASSWORD)))
    session.commit()
    token = client.post("/api/auth/token", data={"username": email, "password": PASSWORD}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin(client, session):
    return _headers_for(client, session, UserRole.Admin)


@pytest.fixture
def operator(client, session):
    return _headers_for(client, session, UserRole.Operator)


@pytest.fixture
def viewer(client, session):
    return _headers_for(client, session, UserRole.Viewer)
