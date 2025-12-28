"""
============================================================================
USER ENDPOINTS
============================================================================
REST API endpoints untuk User management.

Endpoints:
    GET    /users          - Get list of users (admin only)
    POST   /users          - Create new user (admin only)
    GET    /users/me       - Get current user info
    PUT    /users/me       - Update current user
    GET    /users/{id}     - Get specific user (admin only)
    PUT    /users/{id}     - Update specific user (admin only)
    DELETE /users/{id}     - Delete user (admin only)
    POST   /auth/login     - Login to get access token
============================================================================
"""

from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud.crud_user import user as crud_user
from app.models.user import User


# ============================================================================
# ROUTER SETUP
# ============================================================================
# Create router untuk user endpoints
router = APIRouter()


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/auth/login", response_model=schemas.Token)
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login.
    Get access token untuk authenticated requests.
    
    Parameters:
        - username: Email user (OAuth2 menggunakan field 'username')
        - password: Password user
        
    Returns:
        - access_token: JWT token
        - token_type: "bearer"
        
    Example Request:
        POST /api/v1/auth/login
        Content-Type: application/x-www-form-urlencoded
        
        username=user@example.com&password=mypassword
        
    Example Response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        
    Usage:
        Gunakan token untuk authenticated requests:
        Authorization: Bearer <access_token>
    """
    # Authenticate user dengan email & password
    user = crud_user.authenticate(
        db,
        email=form_data.username,  # OAuth2 uses 'username' field
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    elif not crud_user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token = security.create_access_token(subject=user.email)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================================
# CURRENT USER ENDPOINTS
# ============================================================================

@router.get("/users/me", response_model=schemas.User)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get current user information.
    
    Returns:
        User: Current authenticated user
        
    Example Request:
        GET /api/v1/users/me
        Authorization: Bearer <token>
        
    Example Response:
        {
            "id": 1,
            "email": "user@example.com",
            "full_name": "John Doe",
            "is_active": true,
            "is_superuser": false,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
    """
    return current_user


@router.put("/users/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update current user.
    
    Parameters:
        - email: New email (optional)
        - password: New password (optional)
        - full_name: New full name (optional)
        
    Returns:
        User: Updated user
        
    Example Request:
        PUT /api/v1/users/me
        Authorization: Bearer <token>
        Content-Type: application/json
        
        {
            "full_name": "Updated Name",
            "password": "NewPassword123"
        }
        
    Note:
        - Only update fields yang dikirim
        - Password otomatis di-hash
        - Tidak bisa update is_active atau is_superuser sendiri
    """
    # Update user
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user


# ============================================================================
# USER MANAGEMENT ENDPOINTS (Admin Only)
# ============================================================================

@router.get("/users", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Retrieve list of users.
    Admin only endpoint.
    
    Parameters:
        - skip: Number of records to skip (pagination)
        - limit: Maximum number of records to return
        
    Returns:
        List[User]: List of users
        
    Example Request:
        GET /api/v1/users?skip=0&limit=10
        Authorization: Bearer <admin_token>
        
    Example Response:
        [
            {
                "id": 1,
                "email": "user1@example.com",
                "full_name": "User One",
                ...
            },
            {
                "id": 2,
                "email": "user2@example.com",
                "full_name": "User Two",
                ...
            }
        ]
    """
    users = crud_user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Create new user.
    Admin only endpoint.
    
    Parameters:
        - email: User email (required, must be unique)
        - password: User password (required, min 8 chars)
        - full_name: Full name (optional)
        - is_active: Active status (default: true)
        - is_superuser: Superuser status (default: false)
        
    Returns:
        User: Created user
        
    Raises:
        400: If email already registered
        
    Example Request:
        POST /api/v1/users
        Authorization: Bearer <admin_token>
        Content-Type: application/json
        
        {
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "full_name": "New User",
            "is_active": true,
            "is_superuser": false
        }
    """
    # Check if email already exists
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system"
        )
    
    # Create new user
    user = crud_user.create(db, obj_in=user_in)
    return user


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Get user by ID.
    Admin only endpoint.
    
    Parameters:
        - user_id: User ID
        
    Returns:
        User: User with specified ID
        
    Raises:
        404: If user not found
        
    Example Request:
        GET /api/v1/users/1
        Authorization: Bearer <admin_token>
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Update user by ID.
    Admin only endpoint.
    
    Parameters:
        - user_id: User ID to update
        - user_in: User update data
        
    Returns:
        User: Updated user
        
    Raises:
        404: If user not found
        
    Example Request:
        PUT /api/v1/users/1
        Authorization: Bearer <admin_token>
        Content-Type: application/json
        
        {
            "full_name": "Updated Name",
            "is_active": false
        }
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = crud_user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Delete user by ID.
    Admin only endpoint.
    
    WARNING: This is a HARD DELETE. Consider using soft delete instead
    by updating is_active=False.
    
    Parameters:
        - user_id: User ID to delete
        
    Returns:
        User: Deleted user data
        
    Raises:
        404: If user not found
        400: If trying to delete self
        
    Example Request:
        DELETE /api/v1/users/1
        Authorization: Bearer <admin_token>
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users cannot delete themselves"
        )
    
    user = crud_user.remove(db, id=user_id)
    return user


# ============================================================================
# USAGE NOTES
# ============================================================================
"""
Authentication Flow:

1. LOGIN:
    POST /api/v1/auth/login
    Body: username=user@example.com&password=pass123
    
    Response: {"access_token": "...", "token_type": "bearer"}

2. USE TOKEN:
    GET /api/v1/users/me
    Headers: Authorization: Bearer <token>
    
    Response: User data

3. REFRESH TOKEN:
    Untuk production, implement refresh token mechanism.
    Current token berlaku sesuai ACCESS_TOKEN_EXPIRE_MINUTES.

Permission Levels:
    - Public: /auth/login
    - Authenticated: /users/me
    - Admin: /users, /users/{id}

Testing dengan curl:
    # Login
    curl -X POST "http://localhost:8000/api/v1/auth/login" \
         -H "Content-Type: application/x-www-form-urlencoded" \
         -d "username=admin@example.com&password=admin"
    
    # Get current user
    curl -X GET "http://localhost:8000/api/v1/users/me" \
         -H "Authorization: Bearer <token>"
"""