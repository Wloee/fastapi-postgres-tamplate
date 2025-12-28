"""
============================================================================
USER SCHEMAS (Pydantic Models)
============================================================================
Pydantic schemas untuk validasi request/response API.
Schemas ini berbeda dengan SQLAlchemy models:
- SQLAlchemy models: Structure database tables
- Pydantic schemas: Validate & serialize API data

Schemas:
    - UserBase: Base schema dengan common fields
    - UserCreate: Schema untuk create user (input)
    - UserUpdate: Schema untuk update user (input)
    - UserInDBBase: Base schema dengan fields dari database
    - User: Schema untuk response API (output)
    - UserInDB: Schema untuk internal use dengan hashed_password
============================================================================
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    """
    Base schema dengan common fields untuk User.
    Schema lain akan inherit dari ini untuk avoid duplication.
    
    Attributes:
        email (EmailStr): Email user, auto-validated format
        full_name (str, optional): Nama lengkap user
        is_active (bool): Status aktif user
        is_superuser (bool): Flag superuser/admin
    """
    
    email: EmailStr = Field(
        ...,  # Required field
        description="Email user, harus format valid",
        example="user@example.com"
    )
    
    full_name: Optional[str] = Field(
        None,  # Optional field
        max_length=255,
        description="Nama lengkap user",
        example="John Doe"
    )
    
    is_active: bool = Field(
        True,  # Default value
        description="Status aktif user"
    )
    
    is_superuser: bool = Field(
        False,  # Default value
        description="Flag admin dengan full privileges"
    )


# ============================================================================
# CREATE SCHEMA
# ============================================================================

class UserCreate(UserBase):
    """
    Schema untuk create new user.
    Extends UserBase dan menambah field password.
    
    Digunakan untuk:
    - Registration endpoint
    - Admin create user
    
    Attributes:
        password (str): Plaintext password (akan di-hash sebelum save)
        
    Example Request Body:
        {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User",
            "is_active": true,
            "is_superuser": false
        }
    """
    
    password: str = Field(
        ...,  # Required
        min_length=8,  # Minimum 8 characters
        max_length=100,
        description="Password plaintext, min 8 characters",
        example="MySecurePass123!"
    )
    
    # Optional: Override fields from UserBase jika perlu
    # Contoh: email mungkin perlu validasi extra saat create
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "newuser@example.com",
                "password": "securepassword123",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False
            }
        }
    )


# ============================================================================
# UPDATE SCHEMA
# ============================================================================

class UserUpdate(BaseModel):
    """
    Schema untuk update existing user.
    Semua fields optional karena bisa update sebagian data.
    
    Digunakan untuk:
    - Update profile endpoint
    - Admin update user
    
    Note:
        - Password di-handle terpisah untuk security
        - Semua fields optional untuk partial update
        
    Example Request Body (partial update):
        {
            "full_name": "Updated Name"
        }
    """
    
    email: Optional[EmailStr] = Field(
        None,
        description="Email baru jika mau update"
    )
    
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=100,
        description="Password baru jika mau update"
    )
    
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Nama lengkap baru"
    )
    
    is_active: Optional[bool] = Field(
        None,
        description="Update status aktif"
    )
    
    is_superuser: Optional[bool] = Field(
        None,
        description="Update status superuser"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Updated Name",
                "is_active": True
            }
        }
    )


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class UserInDBBase(UserBase):
    """
    Base schema untuk data dari database.
    Include fields yang ada di database tapi tidak di input schemas.
    
    Attributes:
        id (int): User ID dari database
        created_at (datetime): Timestamp pembuatan
        updated_at (datetime): Timestamp update terakhir
    """
    
    id: int = Field(
        ...,
        description="User ID unik",
        example=1
    )
    
    created_at: datetime = Field(
        ...,
        description="Timestamp saat user dibuat"
    )
    
    updated_at: datetime = Field(
        ...,
        description="Timestamp update terakhir"
    )
    
    # Konfigurasi untuk baca data dari ORM model
    model_config = ConfigDict(
        from_attributes=True  # Allow reading data from SQLAlchemy model
    )


class User(UserInDBBase):
    """
    Schema untuk response API ke client.
    Ini yang akan di-return dari endpoints.
    
    TIDAK include hashed_password untuk security.
    
    Usage:
        @app.get("/users/{user_id}", response_model=User)
        def get_user(user_id: int, db: Session = Depends(get_db)):
            user = crud.user.get(db, id=user_id)
            return user  # Auto-converted to User schema
            
    Example Response:
        {
            "id": 1,
            "email": "user@example.com",
            "full_name": "John Doe",
            "is_active": true,
            "is_superuser": false,
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-01T10:00:00"
        }
    """
    pass  # Inherit semua dari UserInDBBase


class UserInDB(UserInDBBase):
    """
    Schema dengan hashed_password untuk internal use.
    JANGAN gunakan sebagai response_model ke client!
    
    Digunakan internal untuk:
    - Password verification
    - Internal operations yang perlu hash
    
    Attributes:
        hashed_password (str): Password yang sudah di-hash
    """
    
    hashed_password: str = Field(
        ...,
        description="Password yang sudah di-hash dengan bcrypt"
    )


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class Token(BaseModel):
    """
    Schema untuk JWT token response.
    
    Digunakan di login endpoint.
    
    Attributes:
        access_token (str): JWT token
        token_type (str): Type of token (always "bearer")
        
    Example Response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    
    access_token: str = Field(
        ...,
        description="JWT access token"
    )
    
    token_type: str = Field(
        default="bearer",
        description="Token type, always 'bearer'"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class TokenPayload(BaseModel):
    """
    Schema untuk JWT token payload.
    
    Digunakan internal untuk decode token.
    
    Attributes:
        sub (str, optional): Subject (user_id atau email)
        exp (int, optional): Expiration timestamp
    """
    
    sub: Optional[str] = Field(
        None,
        description="Subject dari token (user identifier)"
    )
    
    exp: Optional[int] = Field(
        None,
        description="Expiration timestamp"
    )


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
Contoh penggunaan schemas dalam FastAPI endpoints:

1. CREATE USER:
    @app.post("/users", response_model=User)
    def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
        user = crud.user.create(db, obj_in=user_in)
        return user

2. UPDATE USER:
    @app.put("/users/{user_id}", response_model=User)
    def update_user(
        user_id: int,
        user_in: UserUpdate,
        db: Session = Depends(get_db)
    ):
        user = crud.user.update(db, db_obj=user, obj_in=user_in)
        return user

3. GET USER:
    @app.get("/users/{user_id}", response_model=User)
    def get_user(user_id: int, db: Session = Depends(get_db)):
        user = crud.user.get(db, id=user_id)
        return user

Note: FastAPI otomatis convert SQLAlchemy model ke Pydantic schema
"""