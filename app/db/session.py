"""
============================================================================
DATABASE SESSION MODULE
============================================================================
Module ini berisi setup untuk database engine dan session.
SessionLocal adalah factory untuk membuat database sessions.

Components:
    - engine: SQLAlchemy engine untuk koneksi ke database
    - SessionLocal: Session factory untuk create database sessions
    
Usage:
    from app.db.session import SessionLocal
    
    db = SessionLocal()
    try:
        # Gunakan db session
        users = db.query(User).all()
    finally:
        db.close()
============================================================================
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# ============================================================================
# DATABASE ENGINE
# ============================================================================
"""
Create SQLAlchemy engine.

Parameters:
    - connect_args: Extra arguments untuk connection
        - check_same_thread: False untuk SQLite (tidak berlaku untuk PostgreSQL)
    - pool_pre_ping: Test connection sebelum digunakan (berguna untuk long-lived connections)
    - echo: Set True untuk debug SQL queries (print semua query ke console)
"""

engine = create_engine(
    settings.DATABASE_URL,
    # pool_pre_ping: Test koneksi sebelum menggunakan dari pool
    # Berguna untuk menghindari error jika connection sudah closed
    pool_pre_ping=True,
    
    # echo: Print semua SQL statements ke console
    # Set True untuk debugging, False untuk production
    echo=False,
    
    # Pool settings untuk optimize database connections
    # pool_size: Jumlah koneksi yang di-maintain di pool
    pool_size=5,
    
    # max_overflow: Jumlah koneksi tambahan yang bisa dibuat
    # Total max connections = pool_size + max_overflow
    max_overflow=10,
    
    # pool_timeout: Berapa lama (detik) menunggu koneksi dari pool
    pool_timeout=30,
    
    # pool_recycle: Recycle connections setelah X detik
    # Penting untuk PostgreSQL untuk avoid "server closed connection" error
    pool_recycle=3600,  # 1 jam
)


# ============================================================================
# SESSION FACTORY
# ============================================================================
"""
SessionLocal adalah factory class untuk membuat database sessions.

Parameters:
    - autocommit: Jika False, perlu manual commit transactions
    - autoflush: Jika False, perlu manual flush changes ke database
    - bind: Engine yang digunakan untuk koneksi
    
Usage Pattern:
    db = SessionLocal()
    try:
        # Lakukan database operations
        user = db.query(User).first()
        db.commit()  # Commit jika ada changes
    except Exception:
        db.rollback()  # Rollback jika ada error
    finally:
        db.close()  # Selalu close session
"""

SessionLocal = sessionmaker(
    # autocommit=False: Transactions harus di-commit manual
    # Ini lebih aman karena kita punya kontrol penuh
    autocommit=False,
    
    # autoflush=False: Changes tidak otomatis di-flush ke DB
    # Flush manual untuk kontrol lebih baik
    autoflush=False,
    
    # bind: Engine yang digunakan untuk koneksi
    bind=engine,
)


# ============================================================================
# DEPENDENCY FOR FASTAPI
# ============================================================================
def get_db():
    """
    Dependency function untuk FastAPI.
    Function ini akan otomatis:
    1. Create database session
    2. Yield session untuk digunakan
    3. Close session setelah request selesai
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage dalam FastAPI endpoint:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
            
    Benefits:
        - Session otomatis closed setelah request
        - No need manual try/finally
        - Clean dan reusable
        
    Note:
        Function ini akan dipindahkan ke app/api/deps.py
        untuk organization yang lebih baik
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Pastikan session selalu closed
        # Bahkan jika ada error di tengah request
        db.close()


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================
def init_db():
    """
    Initialize database dengan membuat semua tables.
    Function ini biasanya dipanggil saat aplikasi pertama kali dijalankan.
    
    Usage:
        from app.db.session import init_db
        init_db()
        
    Note:
        - Function ini akan create semua tables berdasarkan models
        - Tidak akan error jika table sudah ada
        - Untuk production, gunakan Alembic migrations
    """
    from app.db.base import Base  # Import semua models
    
    # Create semua tables yang belum ada
    # Tidak akan error jika table sudah ada
    Base.metadata.create_all(bind=engine)


# ============================================================================
# TESTING UTILITIES
# ============================================================================
def test_db_connection():
    """
    Test database connection.
    Berguna untuk verify setup database.
    
    Returns:
        bool: True jika koneksi berhasil, False jika gagal
        
    Example:
        >>> from app.db.session import test_db_connection
        >>> if test_db_connection():
        ...     print("Database connected!")
        ... else:
        ...     print("Database connection failed!")
    """
    try:
        # Try untuk execute simple query
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
if __name__ == "__main__":
    """
    Example penggunaan database session.
    Jalankan file ini untuk test koneksi:
        python -m app.db.session
    """
    print("=" * 70)
    print("DATABASE CONNECTION TEST")
    print("=" * 70)
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # Test connection
    if test_db_connection():
        print("✓ Database connection successful!")
    else:
        print("✗ Database connection failed!")
    
    print("=" * 70)