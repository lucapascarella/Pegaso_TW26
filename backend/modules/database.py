from sqlmodel import Session, SQLModel, create_engine

from utils.settings import settings

# check_same_thread=False: FastAPI may use the same SQLite connection from different threads
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)


def create_db_and_tables() -> None:
    """Create the tables that do not exist yet (no migrations: see Alembic for production)."""
    # Import the table models so that SQLModel knows them before create_all
    from modules.models import device  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session():
    """One session per request: opened before the endpoint, closed after the response."""
    with Session(engine) as session:
        yield session
