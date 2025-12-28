"""
============================================================================
DATABASE BASE MODULE
============================================================================
Import semua models di sini untuk Alembic migrations.
Alembic akan detect models yang di-import di file ini.

Usage:
    from app.db.base import Base
    
    # All models are imported and registered
    Base.metadata.create_all(bind=engine)
============================================================================
"""

# Import Base class
from app.db.base_class import Base

# Import all models here untuk Alembic auto-detection
# Setiap kali menambah model baru, import di sini
from app.models.user import User

# Tambahkan import model lain di bawah ini:
# from app.models.post import Post
# from app.models.comment import Comment
# from app.models.category import Category


# ============================================================================
# USAGE NOTES
# ============================================================================
"""
Kenapa perlu file ini?

1. ALEMBIC MIGRATIONS:
   Alembic perlu tahu semua models untuk auto-generate migrations.
   Import semua models di sini agar Alembic bisa detect.

2. CREATE ALL TABLES:
   Saat development, bisa create semua tables dengan:
   from app.db.base import Base
   Base.metadata.create_all(bind=engine)

3. CENTRALIZED MODEL REGISTRY:
   Semua models terdaftar di satu tempat, mudah untuk tracking.

Workflow:

1. Create new model:
   # app/models/post.py
   class Post(Base):
       title = Column(String)
       content = Column(Text)

2. Import di base.py:
   from app.models.post import Post

3. Generate migration:
   alembic revision --autogenerate -m "Add post table"

4. Run migration:
   alembic upgrade head
"""