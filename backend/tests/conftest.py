import os
import sys
import pytest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set test environment flags
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["QDRANT_COLLECTION"] = "test_campus_documents"
os.environ["SECRET_KEY"] = "test_secret_key_for_unit_tests"

from app.db.database import Base, get_db
from app.db.init_db import init_db
from app.db.models import User
from app.core.security import get_password_hash, create_access_token
from app.main import app

# In-memory test SQLite engine
engine_test = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine_test)
    with TestingSessionLocal() as session:
        init_db(session)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db_session():
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(db_session):
    # Ensure admin user exists in session
    admin = db_session.query(User).filter(User.role == "admin").first()
    if not admin:
        admin = User(
            email="admin_test@campushelp.edu",
            hashed_password=get_password_hash("AdminPass123!"),
            full_name="Test Admin",
            role="admin",
            is_active=True
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
    return create_access_token(subject=admin.id, role="admin")


@pytest.fixture
def student_token(db_session):
    student = db_session.query(User).filter(User.role == "student").first()
    if not student:
        student = User(
            email="student_test@campushelp.edu",
            hashed_password=get_password_hash("StudentPass123!"),
            full_name="Test Student",
            role="student",
            is_active=True
        )
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)
    return create_access_token(subject=student.id, role="student")
