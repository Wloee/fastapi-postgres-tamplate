"""
============================================================================
DATABASE BASE CLASS
============================================================================
Module ini berisi base class untuk semua SQLAlchemy models.
Semua model akan inherit dari class ini untuk mendapatkan:
- Automatic table naming
- Common columns (id, created_at, updated_at)
- Utility methods

Usage:
    from app.db.base_class import Base
    
    class User(Base):
        __tablename__ = "users"
        name = Column(String)
============================================================================
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    Base class untuk semua database models.
    
    Setiap model yang inherit dari class ini akan otomatis mendapat:
    1. id: Primary key integer auto-increment
    2. created_at: Timestamp saat record dibuat
    3. updated_at: Timestamp saat record terakhir diupdate
    4. __tablename__: Otomatis generated dari nama class
    
    Attributes:
        id (int): Primary key, auto-increment
        created_at (datetime): Timestamp pembuatan record
        updated_at (datetime): Timestamp update terakhir
    """
    
    # ========================================================================
    # COMMON ATTRIBUTES
    # ========================================================================
    # Atribut ini akan ada di semua table
    
    id: Any  # Type hint untuk id (akan di-set oleh Column)
    __name__: str  # Nama class
    
    # Primary key - auto increment
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Primary key, auto-increment"
    )
    
    # Timestamp saat record dibuat
    # default=datetime.utcnow akan set waktu saat record dibuat
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Timestamp saat record dibuat"
    )
    
    # Timestamp saat record terakhir diupdate
    # onupdate=datetime.utcnow akan update waktu saat record diupdate
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Timestamp saat record terakhir diupdate"
    )
    
    # ========================================================================
    # AUTO TABLE NAMING
    # ========================================================================
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate table name otomatis dari nama class.
        Converts CamelCase ke snake_case dan tambahkan 's' di akhir.
        
        Examples:
            User -> users
            BlogPost -> blog_posts
            UserProfile -> user_profiles
            
        Returns:
            str: Table name dalam format snake_case plural
        """
        # Convert CamelCase ke snake_case
        # Contoh: UserProfile -> user_profile
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        
        # Tambahkan 's' untuk plural (simple pluralization)
        # Note: Ini simple pluralization, untuk kasus kompleks
        # bisa override __tablename__ di model
        return f"{name}s"
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def dict(self) -> dict:
        """
        Convert model instance ke dictionary.
        Berguna untuk serialization atau debugging.
        
        Returns:
            dict: Dictionary representation dari model
            
        Example:
            >>> user = User(name="John", email="john@example.com")
            >>> print(user.dict())
            {'id': 1, 'name': 'John', 'email': 'john@example.com', ...}
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """
        String representation dari model untuk debugging.
        
        Returns:
            str: String representation
            
        Example:
            >>> user = User(id=1, name="John")
            >>> print(user)
            <User(id=1)>
        """
        return f"<{self.__class__.__name__}(id={self.id})>"


# ============================================================================
# USAGE NOTES
# ============================================================================
"""
Cara menggunakan Base class:

1. Import Base:
    from app.db.base_class import Base

2. Buat model dengan inherit Base:
    class User(Base):
        # __tablename__ otomatis jadi 'users'
        name = Column(String(100))
        email = Column(String(255), unique=True)

3. Jika ingin custom table name:
    class User(Base):
        __tablename__ = "my_custom_users_table"
        name = Column(String(100))

4. Semua model otomatis punya:
    - id (primary key)
    - created_at (timestamp pembuatan)
    - updated_at (timestamp update)

5. Utility methods:
    user = session.query(User).first()
    print(user.dict())  # Convert ke dict
    print(user)         # Print representation
"""