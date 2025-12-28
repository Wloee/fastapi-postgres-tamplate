"""
============================================================================
BASE CRUD CLASS
============================================================================
Generic CRUD operations yang reusable untuk semua models.
Class ini menyediakan basic operations: Create, Read, Update, Delete.

Benefits:
    - DRY (Don't Repeat Yourself): Tidak perlu tulis ulang CRUD untuk setiap model
    - Type-safe: Menggunakan Generic types untuk type checking
    - Consistent: Semua CRUD operations punya interface yang sama
    - Extendable: Bisa di-inherit dan override sesuai kebutuhan

Usage:
    from app.crud.base import CRUDBase
    from app.models.user import User
    from app.schemas.user import UserCreate, UserUpdate
    
    user_crud = CRUDBase[User, UserCreate, UserUpdate](User)
    
    # Create
    user = user_crud.create(db, obj_in=user_create_schema)
    
    # Read
    user = user_crud.get(db, id=1)
    users = user_crud.get_multi(db, skip=0, limit=100)
    
    # Update
    user = user_crud.update(db, db_obj=user, obj_in=user_update_schema)
    
    # Delete
    user = user_crud.remove(db, id=1)
============================================================================
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base_class import Base


# ============================================================================
# TYPE VARIABLES
# ============================================================================
# Generic types untuk type checking dan IDE autocomplete

# ModelType: SQLAlchemy model (User, Post, etc.)
ModelType = TypeVar("ModelType", bound=Base)

# CreateSchemaType: Pydantic schema untuk create (UserCreate, PostCreate, etc.)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)

# UpdateSchemaType: Pydantic schema untuk update (UserUpdate, PostUpdate, etc.)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


# ============================================================================
# BASE CRUD CLASS
# ============================================================================

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD class dengan default operations.
    
    Type Parameters:
        ModelType: SQLAlchemy model class
        CreateSchemaType: Pydantic schema untuk create
        UpdateSchemaType: Pydantic schema untuk update
        
    Attributes:
        model: SQLAlchemy model class yang akan di-manage
        
    Example:
        >>> from app.models.user import User
        >>> from app.schemas.user import UserCreate, UserUpdate
        >>> 
        >>> user_crud = CRUDBase[User, UserCreate, UserUpdate](User)
        >>> user = user_crud.get(db, id=1)
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object dengan model.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    # ========================================================================
    # READ OPERATIONS
    # ========================================================================
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get single record by ID.
        
        Args:
            db (Session): Database session
            id (Any): Primary key value
            
        Returns:
            ModelType | None: Model instance jika found, None jika tidak
            
        Example:
            >>> user = crud.user.get(db, id=1)
            >>> if user:
            ...     print(user.email)
            ... else:
            ...     print("User not found")
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records dengan pagination.
        
        Args:
            db (Session): Database session
            skip (int): Number of records to skip (offset)
            limit (int): Maximum number of records to return
            
        Returns:
            List[ModelType]: List of model instances
            
        Example:
            >>> # Get first 10 users
            >>> users = crud.user.get_multi(db, skip=0, limit=10)
            >>> 
            >>> # Get next 10 users (pagination)
            >>> users = crud.user.get_multi(db, skip=10, limit=10)
            
        Note:
            - Default limit is 100 untuk prevent large queries
            - Use skip dan limit untuk implement pagination
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    # ========================================================================
    # CREATE OPERATION
    # ========================================================================
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create new record.
        
        Args:
            db (Session): Database session
            obj_in (CreateSchemaType): Pydantic schema dengan data untuk create
            
        Returns:
            ModelType: Created model instance dengan ID dari database
            
        Example:
            >>> from app.schemas.user import UserCreate
            >>> 
            >>> user_in = UserCreate(
            ...     email="new@example.com",
            ...     password="password123",
            ...     full_name="New User"
            ... )
            >>> user = crud.user.create(db, obj_in=user_in)
            >>> print(user.id)  # Auto-generated ID
            
        Note:
            - Method ini auto-commit ke database
            - ID akan di-generate otomatis
            - created_at dan updated_at di-set otomatis
        """
        # Convert Pydantic schema ke dict
        obj_in_data = jsonable_encoder(obj_in)
        
        # Create model instance dari dict
        db_obj = self.model(**obj_in_data)
        
        # Add ke session dan commit
        db.add(db_obj)
        db.commit()
        
        # Refresh untuk get generated values (id, timestamps)
        db.refresh(db_obj)
        
        return db_obj
    
    # ========================================================================
    # UPDATE OPERATION
    # ========================================================================
    
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update existing record.
        
        Args:
            db (Session): Database session
            db_obj (ModelType): Existing model instance dari database
            obj_in (UpdateSchemaType | dict): Data untuk update
            
        Returns:
            ModelType: Updated model instance
            
        Example:
            >>> from app.schemas.user import UserUpdate
            >>> 
            >>> # Get existing user
            >>> user = crud.user.get(db, id=1)
            >>> 
            >>> # Prepare update data
            >>> user_update = UserUpdate(full_name="Updated Name")
            >>> 
            >>> # Update
            >>> updated_user = crud.user.update(db, db_obj=user, obj_in=user_update)
            >>> print(updated_user.full_name)  # "Updated Name"
            
        Note:
            - Only update fields yang ada di obj_in
            - Fields yang tidak di-set di obj_in tidak akan berubah
            - updated_at timestamp otomatis di-update
        """
        # Get data dari existing object
        obj_data = jsonable_encoder(db_obj)
        
        # Convert update schema ke dict
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # Update hanya fields yang ada di update_data
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        # Commit changes
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    # ========================================================================
    # DELETE OPERATION
    # ========================================================================
    
    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        """
        Delete record by ID.
        
        Args:
            db (Session): Database session
            id (int): ID of record to delete
            
        Returns:
            ModelType | None: Deleted model instance jika found, None jika tidak
            
        Example:
            >>> # Hard delete user
            >>> deleted_user = crud.user.remove(db, id=1)
            >>> if deleted_user:
            ...     print(f"Deleted user: {deleted_user.email}")
            ... else:
            ...     print("User not found")
            
        Warning:
            - Ini adalah HARD DELETE (permanent)
            - Untuk soft delete, gunakan update dengan is_active=False
            - Consider cascade deletes jika ada foreign key relationships
        """
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


# ============================================================================
# USAGE NOTES
# ============================================================================
"""
Best Practices:

1. INHERIT untuk custom operations:
    class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
        def get_by_email(self, db: Session, email: str):
            return db.query(User).filter(User.email == email).first()
    
    user = CRUDUser(User)

2. ERROR HANDLING:
    try:
        user = crud.user.create(db, obj_in=user_in)
    except IntegrityError:
        # Handle duplicate email, etc.
        pass

3. SOFT DELETE instead of hard delete:
    # Instead of: crud.user.remove(db, id=1)
    # Use:
    user = crud.user.get(db, id=1)
    crud.user.update(db, db_obj=user, obj_in={"is_active": False})

4. PAGINATION:
    # Get page 1 (first 20 items)
    users = crud.user.get_multi(db, skip=0, limit=20)
    
    # Get page 2 (next 20 items)
    users = crud.user.get_multi(db, skip=20, limit=20)

5. FILTERING:
    # For complex queries, create custom methods:
    class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
        def get_active_users(self, db: Session):
            return db.query(User).filter(User.is_active == True).all()
"""