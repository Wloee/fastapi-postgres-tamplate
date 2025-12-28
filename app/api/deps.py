"""
============================================================================
API DEPENDENCIES
============================================================================
Module ini berisi dependency functions untuk FastAPI endpoints.
Dependencies digunakan untuk:
- Database session management
- Authentication & authorization
- Request validation
- Reusable logic across endpoints

Usage dengan Depends():
    @app.get("/users/me")
    def get_current_user(
        current_user: User = Depends(get_current_active_user)
    ):
        return current_user
============================================================================
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.crud.crud_user import user as crud_user
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.user import TokenPayload


# ============================================================================
# OAUTH2 SCHEME
# ============================================================================
"""
OAuth2PasswordBearer adalah dependency untuk extract token dari header.
Token harus dikirim dalam format:
    Authorization: Bearer <token>

tokenUrl: URL endpoint untuk login/get token
"""
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


# ============================================================================
# DATABASE SESSION DEPENDENCY
# ============================================================================

def get_db() -> Generator:
    """
    Dependency untuk mendapatkan database session.
    
    Session lifecycle:
    1. Create session
    2. Yield session untuk digunakan
    3. Close session setelah request selesai (auto)
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
            
    Benefits:
        - Auto session management
        - No need manual try/finally
        - Session always closed after request
        - Connection pooling handled automatically
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get current authenticated user dari JWT token.
    
    Process:
    1. Extract token dari Authorization header
    2. Decode & validate token
    3. Get user dari database
    4. Return user jika valid
    
    Args:
        db (Session): Database session
        token (str): JWT token dari Authorization header
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException(401): Jika token invalid atau user tidak found
        
    Usage:
        @app.get("/users/me")
        def read_users_me(
            current_user: User = Depends(get_current_user)
        ):
            return current_user
            
    Token Format:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    # Exception untuk unauthorized
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract user identifier dari token
        token_data = TokenPayload(**payload)
        
        if token_data.sub is None:
            raise credentials_exception
            
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Get user dari database
    user = crud_user.get_by_email(db, email=token_data.sub)
    
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user dan verify bahwa user aktif.
    
    Args:
        current_user (User): Current user dari get_current_user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException(400): Jika user tidak aktif/disabled
        
    Usage:
        @app.get("/protected-resource")
        def protected_route(
            current_user: User = Depends(get_current_active_user)
        ):
            # Only active users can access this
            return {"message": "Success"}
            
    Note:
        Dependency ini chain dengan get_current_user:
        1. get_current_user: Validate token & get user
        2. get_current_active_user: Check if user is active
    """
    if not crud_user.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user dan verify bahwa user adalah superuser/admin.
    
    Args:
        current_user (User): Current user dari get_current_user
        
    Returns:
        User: Current superuser
        
    Raises:
        HTTPException(403): Jika user bukan superuser
        
    Usage:
        @app.delete("/users/{user_id}")
        def delete_user(
            user_id: int,
            current_user: User = Depends(get_current_active_superuser)
        ):
            # Only superusers can delete users
            # Delete user logic here
            pass
            
    Note:
        Use dependency ini untuk endpoints yang hanya boleh diakses admin.
        Contoh use cases:
        - Delete user
        - View all users
        - Modify system settings
        - Access admin dashboard
    """
    if not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


# ============================================================================
# OPTIONAL AUTHENTICATION
# ============================================================================

def get_current_user_optional(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """
    Get current user jika ada token, None jika tidak ada.
    Berguna untuk endpoints yang bisa diakses dengan atau tanpa auth.
    
    Args:
        db (Session): Database session
        token (str, optional): JWT token jika ada
        
    Returns:
        User | None: User jika authenticated, None jika tidak
        
    Usage:
        @app.get("/posts")
        def get_posts(
            current_user: Optional[User] = Depends(get_current_user_optional)
        ):
            if current_user:
                # Show user's private posts too
                posts = get_all_posts_including_private(current_user.id)
            else:
                # Show only public posts
                posts = get_public_posts()
            return posts
            
    Note:
        Tidak throw exception jika token invalid atau tidak ada.
        Perfect untuk public endpoints dengan optional auth features.
    """
    if not token:
        return None
    
    try:
        return get_current_user(db=db, token=token)
    except HTTPException:
        return None


# ============================================================================
# CUSTOM DEPENDENCIES
# ============================================================================

def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
) -> User:
    """
    Get user by ID dengan validation.
    
    Args:
        user_id (int): User ID dari path parameter
        db (Session): Database session
        
    Returns:
        User: User instance
        
    Raises:
        HTTPException(404): Jika user tidak found
        
    Usage:
        @app.get("/users/{user_id}")
        def get_user(user: User = Depends(get_user_by_id)):
            return user
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


# ============================================================================
# USAGE PATTERNS
# ============================================================================
"""
Common dependency patterns dalam FastAPI:

1. PUBLIC ENDPOINT (No auth required):
    @app.get("/public")
    def public_endpoint():
        return {"message": "Public access"}

2. AUTHENTICATED ENDPOINT:
    @app.get("/protected")
    def protected_endpoint(
        current_user: User = Depends(get_current_active_user)
    ):
        return {"user": current_user.email}

3. ADMIN ONLY ENDPOINT:
    @app.delete("/admin/users/{user_id}")
    def admin_delete_user(
        user_id: int,
        current_user: User = Depends(get_current_active_superuser),
        db: Session = Depends(get_db)
    ):
        crud_user.remove(db, id=user_id)
        return {"message": "User deleted"}

4. OPTIONAL AUTH ENDPOINT:
    @app.get("/posts")
    def get_posts(
        current_user: Optional[User] = Depends(get_current_user_optional)
    ):
        if current_user:
            return {"posts": "including private"}
        return {"posts": "public only"}

5. MULTIPLE DEPENDENCIES:
    @app.put("/users/{user_id}")
    def update_user(
        user: User = Depends(get_user_by_id),
        user_in: UserUpdate = ...,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        # Verify permission
        if user.id != current_user.id and not current_user.is_superuser:
            raise HTTPException(403, "Not enough permissions")
        
        # Update user
        return crud_user.update(db, db_obj=user, obj_in=user_in)
"""