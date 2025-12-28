"""
============================================================================
USER CRUD OPERATIONS
============================================================================
Specialized CRUD operations untuk User model.
Extends CRUDBase dengan user-specific operations.

Custom operations:
    - get_by_email: Get user by email
    - create_with_hashed_password: Create user dengan auto password hashing
    - authenticate: Authenticate user dengan email & password
    - update_password: Update password user
============================================================================
"""

from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations untuk User dengan custom methods.
    
    Inherits from:
        CRUDBase: Get basic CRUD operations (get, get_multi, create, update, remove)
        
    Additional methods:
        - get_by_email: Find user by email
        - create: Override untuk auto hash password
        - authenticate: Verify credentials
        - is_active: Check user status
        - is_superuser: Check admin status
    """
    
    # ========================================================================
    # READ OPERATIONS
    # ========================================================================
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            db (Session): Database session
            email (str): User's email address
            
        Returns:
            User | None: User instance jika found, None jika tidak
            
        Example:
            >>> user = crud.user.get_by_email(db, email="john@example.com")
            >>> if user:
            ...     print(f"Found user: {user.full_name}")
            ... else:
            ...     print("User not found")
            
        Note:
            Email di-query case-sensitive. Consider normalize email ke lowercase.
        """
        return db.query(User).filter(User.email == email).first()
    
    # ========================================================================
    # CREATE OPERATION
    # ========================================================================
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create new user dengan auto password hashing.
        Override dari CRUDBase.create untuk handle password hashing.
        
        Args:
            db (Session): Database session
            obj_in (UserCreate): User data dengan plaintext password
            
        Returns:
            User: Created user instance
            
        Example:
            >>> from app.schemas.user import UserCreate
            >>> 
            >>> user_in = UserCreate(
            ...     email="new@example.com",
            ...     password="MySecurePass123!",
            ...     full_name="John Doe"
            ... )
            >>> user = crud.user.create(db, obj_in=user_in)
            >>> 
            >>> # Password sudah di-hash otomatis
            >>> print(user.hashed_password[:20])  # $2b$12$...
            
        Security Notes:
            - Password plaintext langsung di-hash dengan bcrypt
            - Plaintext password TIDAK disimpan ke database
            - Hash menggunakan salt yang random setiap kali
        """
        # Create dict dari schema dan hash password
        create_data = obj_in.model_dump()
        create_data.pop("password")  # Remove plaintext password
        
        # Create user dengan hashed password
        db_obj = User(
            **create_data,
            hashed_password=get_password_hash(obj_in.password)
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    # ========================================================================
    # UPDATE OPERATIONS
    # ========================================================================
    
    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update user dengan auto password hashing.
        Override dari CRUDBase.update untuk handle password update.
        
        Args:
            db (Session): Database session
            db_obj (User): Existing user instance
            obj_in (UserUpdate | dict): Update data
            
        Returns:
            User: Updated user instance
            
        Example:
            >>> from app.schemas.user import UserUpdate
            >>> 
            >>> # Get user
            >>> user = crud.user.get(db, id=1)
            >>> 
            >>> # Update name dan password
            >>> user_update = UserUpdate(
            ...     full_name="Updated Name",
            ...     password="NewPassword123!"
            ... )
            >>> updated_user = crud.user.update(db, db_obj=user, obj_in=user_update)
            
        Note:
            - Jika ada field 'password', akan di-hash otomatis
            - Fields lain di-update seperti biasa
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # Hash password jika ada di update data
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    # ========================================================================
    # AUTHENTICATION
    # ========================================================================
    
    def authenticate(
        self, 
        db: Session, 
        *, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """
        Authenticate user dengan email dan password.
        
        Args:
            db (Session): Database session
            email (str): User's email
            password (str): Plaintext password
            
        Returns:
            User | None: User instance jika credentials valid, None jika tidak
            
        Example:
            >>> # Login attempt
            >>> user = crud.user.authenticate(
            ...     db,
            ...     email="john@example.com",
            ...     password="userpassword"
            ... )
            >>> 
            >>> if user:
            ...     print("Login successful!")
            ... else:
            ...     print("Invalid credentials")
            
        Security Notes:
            - Password verification menggunakan bcrypt
            - Return None jika user tidak found ATAU password salah
            - Tidak memberikan hint apakah email atau password yang salah
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    # ========================================================================
    # STATUS CHECKS
    # ========================================================================
    
    def is_active(self, user: User) -> bool:
        """
        Check apakah user aktif.
        
        Args:
            user (User): User instance
            
        Returns:
            bool: True jika active, False jika disabled
            
        Example:
            >>> user = crud.user.get(db, id=1)
            >>> if crud.user.is_active(user):
            ...     # Allow access
            ...     pass
            ... else:
            ...     # Reject access
            ...     raise HTTPException(status_code=400, detail="Inactive user")
        """
        return user.is_active
    
    def is_superuser(self, user: User) -> bool:
        """
        Check apakah user adalah superuser/admin.
        
        Args:
            user (User): User instance
            
        Returns:
            bool: True jika superuser, False jika bukan
            
        Example:
            >>> user = crud.user.get(db, id=1)
            >>> if crud.user.is_superuser(user):
            ...     # Grant admin access
            ...     pass
            ... else:
            ...     # Regular user access
            ...     pass
        """
        return user.is_superuser


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
# Create instance yang akan digunakan di seluruh aplikasi
# Import di module lain dengan:
#   from app.crud.crud_user import user
user = CRUDUser(User)


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
Example penggunaan dalam FastAPI endpoints:

1. CREATE USER:
    from app.crud.crud_user import user as crud_user
    
    @app.post("/users", response_model=User)
    def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
        # Check if email already exists
        existing_user = crud_user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user (password auto-hashed)
        user = crud_user.create(db, obj_in=user_in)
        return user

2. LOGIN/AUTHENTICATION:
    @app.post("/login", response_model=Token)
    def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
        # Authenticate user
        user = crud_user.authenticate(
            db,
            email=form_data.username,
            password=form_data.password
        )
        
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        elif not crud_user.is_active(user):
            raise HTTPException(status_code=400, detail="Inactive user")
        
        # Create access token
        access_token = create_access_token(subject=user.email)
        return {"access_token": access_token, "token_type": "bearer"}

3. UPDATE USER:
    @app.put("/users/{user_id}", response_model=User)
    def update_user(
        user_id: int,
        user_in: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        # Get existing user
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check permission
        if not crud_user.is_superuser(current_user) and current_user.id != user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        # Update user (password auto-hashed if provided)
        user = crud_user.update(db, db_obj=user, obj_in=user_in)
        return user
"""