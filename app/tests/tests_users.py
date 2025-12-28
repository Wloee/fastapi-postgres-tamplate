"""
============================================================================
USER ENDPOINT TESTS
============================================================================
Unit tests dan integration tests untuk user endpoints.

Test categories:
    - Authentication tests
    - User CRUD tests
    - Permission tests
    - Validation tests

Run tests:
    pytest tests/test_users.py
    pytest tests/test_users.py -v  # verbose
    pytest tests/test_users.py -k "test_create_user"  # specific test
============================================================================
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base_class import Base
from app.api import deps
from app.core.config import settings


# ============================================================================
# TEST DATABASE SETUP
# ============================================================================
"""
Setup test database yang terpisah dari production database.
Menggunakan SQLite in-memory untuk speed.
"""

# SQLite in-memory database untuk testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def db():
    """
    Create test database dan cleanup setelah test.
    
    Yields:
        Session: Test database session
        
    Usage:
        def test_something(db):
            user = User(email="test@example.com")
            db.add(user)
            db.commit()
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables setelah test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create test client dengan test database.
    
    Args:
        db: Test database session dari fixture
        
    Yields:
        TestClient: FastAPI test client
        
    Usage:
        def test_endpoint(client):
            response = client.get("/api/v1/users/me")
            assert response.status_code == 200
    """
    # Override get_db dependency dengan test database
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[deps.get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as c:
        yield c
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """
    Sample user data untuk testing.
    
    Returns:
        dict: User data
    """
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False
    }


@pytest.fixture
def test_superuser_data():
    """
    Sample superuser data untuk testing.
    
    Returns:
        dict: Superuser data
    """
    return {
        "email": "admin@example.com",
        "password": "adminpassword123",
        "full_name": "Admin User",
        "is_active": True,
        "is_superuser": True
    }


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

def test_login_success(client, test_user_data):
    """
    Test successful login.
    """
    # Create user first
    client.post("/api/v1/users", json=test_user_data)
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user_data):
    """
    Test login dengan password salah.
    """
    # Create user
    client.post("/api/v1/users", json=test_user_data)
    
    # Login dengan wrong password
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_user(client):
    """
    Test login dengan user yang tidak exist.
    """
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 400


# ============================================================================
# USER CRUD TESTS
# ============================================================================

def test_create_user(client, test_user_data):
    """
    Test create new user.
    """
    response = client.post("/api/v1/users", json=test_user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["full_name"] == test_user_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data  # Password tidak di-expose


def test_create_duplicate_user(client, test_user_data):
    """
    Test create user dengan email yang sudah exist.
    """
    # Create first user
    client.post("/api/v1/users", json=test_user_data)
    
    # Try create duplicate
    response = client.post("/api/v1/users", json=test_user_data)
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_current_user(client, test_user_data):
    """
    Test get current user info.
    """
    # Create and login
    client.post("/api/v1/users", json=test_user_data)
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]


def test_update_current_user(client, test_user_data):
    """
    Test update current user.
    """
    # Create and login
    client.post("/api/v1/users", json=test_user_data)
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    token = login_response.json()["access_token"]
    
    # Update user
    update_data = {"full_name": "Updated Name"}
    response = client.put(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"


# ============================================================================
# PERMISSION TESTS
# ============================================================================

def test_get_users_unauthorized(client):
    """
    Test get users tanpa authentication.
    """
    response = client.get("/api/v1/users")
    assert response.status_code == 401


def test_get_users_non_admin(client, test_user_data):
    """
    Test get users dengan non-admin user.
    """
    # Create and login as regular user
    client.post("/api/v1/users", json=test_user_data)
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    token = login_response.json()["access_token"]
    
    # Try get all users (should fail)
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403


def test_get_users_as_admin(client, test_superuser_data):
    """
    Test get users dengan admin user.
    """
    # Create and login as admin
    client.post("/api/v1/users", json=test_superuser_data)
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_superuser_data["email"],
            "password": test_superuser_data["password"]
        }
    )
    token = login_response.json()["access_token"]
    
    # Get all users (should succeed)
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# ============================================================================
# VALIDATION TESTS
# ============================================================================

def test_create_user_invalid_email(client):
    """
    Test create user dengan invalid email.
    """
    invalid_data = {
        "email": "not-an-email",
        "password": "password123",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/users", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_create_user_short_password(client):
    """
    Test create user dengan password terlalu pendek.
    """
    invalid_data = {
        "email": "test@example.com",
        "password": "short",  # Less than 8 characters
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/users", json=invalid_data)
    assert response.status_code == 422


def test_create_user_missing_required_field(client):
    """
    Test create user tanpa required field.
    """
    invalid_data = {
        "email": "test@example.com"
        # Missing password
    }
    
    response = client.post("/api/v1/users", json=invalid_data)
    assert response.status_code == 422


# ============================================================================
# PAGINATION TESTS
# ============================================================================

def test_get_users_pagination(client, test_superuser_data):
    """
    Test pagination pada get users.
    """
    # Create admin
    client.post("/api/v1/users", json=test_superuser_data)
    
    # Create multiple users
    for i in range(5):
        user_data = {
            "email": f"user{i}@example.com",
            "password": "password123",
            "full_name": f"User {i}"
        }
        client.post("/api/v1/users", json=user_data)
    
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_superuser_data["email"],
            "password": test_superuser_data["password"]
        }
    )
    token = login_response.json()["access_token"]
    
    # Get first 2 users
    response = client.get(
        "/api/v1/users?skip=0&limit=2",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


# ============================================================================
# USAGE NOTES
# ============================================================================
"""
Running Tests:

1. RUN ALL TESTS:
   pytest tests/

2. RUN SPECIFIC FILE:
   pytest tests/test_users.py

3. RUN SPECIFIC TEST:
   pytest tests/test_users.py::test_create_user

4. RUN WITH VERBOSE OUTPUT:
   pytest tests/ -v

5. RUN WITH COVERAGE:
   pytest --cov=app tests/
   pytest --cov=app --cov-report=html tests/

6. RUN AND STOP ON FIRST FAILURE:
   pytest tests/ -x

7. RUN TESTS MATCHING PATTERN:
   pytest tests/ -k "login"

Test Structure:

1. ARRANGE: Setup test data dan preconditions
2. ACT: Execute the code being tested
3. ASSERT: Verify results

Example:
    def test_example():
        # Arrange
        user_data = {"email": "test@example.com"}
        
        # Act
        response = client.post("/api/v1/users", json=user_data)
        
        # Assert
        assert response.status_code == 201

Best Practices:

1. Test isolation - each test should be independent
2. Use fixtures untuk reusable setup
3. Clear test names - describe what's being tested
4. Test both success dan failure cases
5. Don't test external dependencies (mock them)
6. Keep tests simple dan focused
7. Use parametrize untuk test multiple scenarios

Fixtures Benefits:

1. Reusable setup code
2. Automatic cleanup
3. Dependency injection
4. Scope control (function, class, module, session)

Coverage:

Aim for:
- 80%+ code coverage
- 100% coverage untuk critical paths
- Test edge cases dan error handling

Continuous Integration:

Add to CI/CD pipeline:
    - pytest tests/ --cov=app --cov-fail-under=80
    - Fails if coverage < 80%
"""