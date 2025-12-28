"""
============================================================================
USER MODEL
============================================================================
SQLAlchemy model untuk table users.
Model ini merepresentasikan struktur table di database.

Table columns:
    - id: Primary key (inherited from Base)
    - email: Email user (unique)
    - hashed_password: Password yang sudah di-hash
    - full_name: Nama lengkap user
    - is_active: Status aktif user
    - is_superuser: Apakah user adalah superuser/admin
    - created_at: Timestamp dibuat (inherited from Base)
    - updated_at: Timestamp update (inherited from Base)
============================================================================
"""

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    """
    User model untuk authentication dan user management.
    
    Attributes:
        email (str): Email user, harus unique
        hashed_password (str): Password yang sudah di-hash (jangan simpan plaintext!)
        full_name (str): Nama lengkap user, optional
        is_active (bool): Status aktif user, default True
        is_superuser (bool): Flag untuk admin/superuser, default False
        
    Inherited from Base:
        id (int): Primary key, auto-increment
        created_at (datetime): Waktu pembuatan record
        updated_at (datetime): Waktu update terakhir
        
    Example:
        >>> user = User(
        ...     email="john@example.com",
        ...     hashed_password="$2b$12$...",
        ...     full_name="John Doe",
        ...     is_active=True
        ... )
        >>> db.add(user)
        >>> db.commit()
    """
    
    # ========================================================================
    # TABLE NAME
    # ========================================================================
    # Otomatis jadi 'users' dari Base class
    # Bisa di-override jika ingin nama berbeda:
    # __tablename__ = "my_users"
    
    # ========================================================================
    # COLUMNS
    # ========================================================================
    
    # Email - unique dan indexed untuk performa query
    email = Column(
        String(255),           # Max length 255 characters
        unique=True,           # Email harus unique
        index=True,            # Create index untuk performa query
        nullable=False,        # Email wajib diisi
        comment="Email user, harus unique"
    )
    
    # Hashed Password - JANGAN simpan plaintext password!
    hashed_password = Column(
        String(255),           # Max length untuk hashed password
        nullable=False,        # Password wajib ada
        comment="Password yang sudah di-hash menggunakan bcrypt"
    )
    
    # Full Name - optional
    full_name = Column(
        String(255),
        nullable=True,         # Boleh null/kosong
        comment="Nama lengkap user"
    )
    
    # Is Active - untuk soft delete atau disable user
    is_active = Column(
        Boolean,
        default=True,          # Default user aktif
        nullable=False,
        comment="Status aktif user. False = disabled/deleted"
    )
    
    # Is Superuser - untuk permission admin
    is_superuser = Column(
        Boolean,
        default=False,         # Default bukan superuser
        nullable=False,
        comment="Flag admin/superuser dengan full access"
    )
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    # Jika ada table lain yang berelasi dengan User, define di sini
    # Contoh:
    # posts = relationship("Post", back_populates="author")
    # comments = relationship("Comment", back_populates="user")
    
    # ========================================================================
    # METHODS
    # ========================================================================
    
    def __repr__(self) -> str:
        """
        String representation untuk debugging.
        
        Returns:
            str: Informasi user untuk debugging
            
        Example:
            >>> user = User(id=1, email="john@example.com")
            >>> print(user)
            <User(id=1, email='john@example.com')>
        """
        return f"<User(id={self.id}, email='{self.email}')>"
    
    def is_admin(self) -> bool:
        """
        Check apakah user adalah admin/superuser.
        
        Returns:
            bool: True jika superuser, False jika bukan
            
        Example:
            >>> if user.is_admin():
            ...     print("User has admin privileges")
        """
        return self.is_superuser
    
    def can_access(self) -> bool:
        """
        Check apakah user bisa akses sistem.
        User harus aktif untuk bisa akses.
        
        Returns:
            bool: True jika aktif, False jika disabled
            
        Example:
            >>> if user.can_access():
            ...     # Allow user to login
            ... else:
            ...     # Reject login
        """
        return self.is_active


# ============================================================================
# MODEL USAGE NOTES
# ============================================================================
"""
Best Practices untuk User Model:

1. PASSWORD SECURITY:
   - JANGAN PERNAH simpan plaintext password
   - Selalu hash password sebelum save
   - Gunakan bcrypt untuk hashing (di app/core/security.py)
   
   Example:
       from app.core.security import get_password_hash
       user.hashed_password = get_password_hash("mypassword")

2. EMAIL VALIDATION:
   - Validasi format email sebelum save
   - Email harus unique
   - Consider case-insensitive email
   
   Example:
       user.email = user.email.lower()  # Normalize ke lowercase

3. SOFT DELETE:
   - Gunakan is_active=False untuk "delete" user
   - Jangan hard delete untuk maintain data integrity
   
   Example:
       user.is_active = False  # Soft delete
       db.commit()

4. PERMISSIONS:
   - is_superuser untuk admin privileges
   - Bisa ditambah custom permissions sesuai kebutuhan
   
   Example:
       if user.is_superuser:
           # Allow access to admin panel

5. QUERIES:
   - Email di-index untuk performa
   - Use filter untuk query by email
   
   Example:
       user = db.query(User).filter(User.email == email).first()
"""