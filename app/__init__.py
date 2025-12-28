"""
============================================================================
__init__.py FILES FOR ALL PACKAGES
============================================================================
File ini berisi semua __init__.py yang dibutuhkan untuk structure project.
Buat file-file ini di folder masing-masing.
============================================================================
"""

# ============================================================================
# app/__init__.py
# ============================================================================
"""
Main application package.
"""
# Empty file or add package-level imports if needed


# ============================================================================
# app/api/__init__.py
# ============================================================================
"""
API package containing all API related modules.
"""


# ============================================================================
# app/api/v1/__init__.py
# ============================================================================
"""
API version 1 package.
"""


# ============================================================================
# app/api/v1/endpoints/__init__.py
# ============================================================================
"""
API endpoints package.
All endpoint modules should be imported here.
"""

# Optional: Import all routers untuk easy access
# from .users import router as users_router


# ============================================================================
# app/core/__init__.py
# ============================================================================
"""
Core package containing configuration and utilities.
"""


# ============================================================================
# app/db/__init__.py
# ============================================================================
"""
Database package containing database setup and models.
"""


# ============================================================================
# app/models/__init__.py
# ============================================================================
"""
SQLAlchemy models package.
Import all models here untuk easy access.
"""

from .user import User

# Export models untuk easy import
__all__ = ["User"]


# ============================================================================
# app/schemas/__init__.py
# ============================================================================
"""
Pydantic schemas package.
Import all schemas here untuk easy access.
"""

from .user import (
    User,
    UserCreate,
    UserUpdate,
    UserInDB,
    Token,
    TokenPayload,
)

# Export schemas untuk easy import
__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "Token",
    "TokenPayload",
]


# ============================================================================
# app/crud/__init__.py
# ============================================================================
"""
CRUD operations package.
Import all CRUD objects here untuk easy access.
"""

from .crud_user import user

# Export CRUD objects
__all__ = ["user"]


# ============================================================================
# app/services/__init__.py
# ============================================================================
"""
Business logic services package.
Import all services here.
"""


# ============================================================================
# tests/__init__.py
# ============================================================================
"""
Tests package.
"""


# ============================================================================
# USAGE NOTES
# ============================================================================
"""
Purpose of __init__.py files:

1. MARK AS PYTHON PACKAGE:
   Python treats directories with __init__.py as packages.
   Without it, Python won't recognize the directory as a package.

2. PACKAGE INITIALIZATION:
   Code in __init__.py runs when package is imported.
   Useful untuk:
   - Package-level initialization
   - Import commonly used items
   - Define package-level variables

3. SIMPLIFY IMPORTS:
   Instead of:
       from app.models.user import User
       from app.models.post import Post
   
   Can do:
       from app.models import User, Post

4. CONTROL NAMESPACE:
   Use __all__ untuk explicitly define what's exported:
       __all__ = ["User", "Post"]

Example Usage:

# Before (without __init__.py imports):
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.crud.crud_user import user as crud_user

# After (with __init__.py imports):
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.crud import user as crud_user

Best Practices:

1. Keep __init__.py files simple
2. Only import frequently used items
3. Use __all__ untuk explicit exports
4. Avoid circular imports
5. Don't put business logic here

Common Patterns:

1. EMPTY __init__.py:
   # Just mark as package
   # No imports needed

2. RE-EXPORT PATTERN:
   from .user import User
   from .post import Post
   __all__ = ["User", "Post"]

3. PACKAGE-LEVEL CONFIG:
   # Configuration atau constants
   VERSION = "1.0.0"
   DEFAULT_TIMEOUT = 30

4. LAZY IMPORTS:
   def get_user_model():
       from .user import User
       return User

5. SUBPACKAGE EXPOSURE:
   from .api import router
   from .models import Base
   __all__ = ["router", "Base"]
"""