"""
============================================================================
ALEMBIC ENVIRONMENT CONFIGURATION
============================================================================
File ini mengkonfigurasi Alembic untuk database migrations.

Key configurations:
    - Import all models untuk auto-detection
    - Get database URL dari environment variables
    - Configure migration context
    
DO NOT modify this file unless you know what you're doing!
============================================================================
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# ============================================================================
# IMPORT APPLICATION COMPONENTS
# ============================================================================
# Import Base yang sudah include semua models
from app.db.base import Base

# Import settings untuk database URL
from app.core.config import settings


# ============================================================================
# ALEMBIC CONFIG
# ============================================================================
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ============================================================================
# TARGET METADATA
# ============================================================================
# Add your model's MetaData object here for 'autogenerate' support
# 
# IMPORTANT: Base.metadata berisi semua models yang di-import di app.db.base
# Pastikan semua models sudah di-import di app/db/base.py
target_metadata = Base.metadata

# ============================================================================
# OTHER VALUES FROM CONFIG
# ============================================================================
# Other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """
    Get database URL dari environment variables.
    
    Returns:
        str: Database connection URL
        
    Note:
        Database URL diambil dari settings yang load dari .env file.
        Format: postgresql://user:pass@host:port/dbname
    """
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    
    Usage:
        Offline mode is useful untuk generate SQL scripts
        tanpa koneksi ke database.
        
        alembic upgrade head --sql > migration.sql
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # ========================================================================
        # MIGRATION OPTIONS
        # ========================================================================
        # compare_type: Compare column types during autogenerate
        compare_type=True,
        
        # compare_server_default: Compare server defaults
        compare_server_default=True,
        
        # include_schemas: Include all schemas
        include_schemas=False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine
    and associate a connection with the context.
    
    This is the normal mode untuk apply migrations ke database.
    
    Usage:
        Normal migration commands akan use online mode:
        
        alembic upgrade head
        alembic downgrade -1
    """
    # ========================================================================
    # CONFIGURATION
    # ========================================================================
    configuration = config.get_section(config.config_ini_section)
    
    # Override sqlalchemy.url dari config file dengan URL dari environment
    configuration["sqlalchemy.url"] = get_url()
    
    # ========================================================================
    # CREATE ENGINE
    # ========================================================================
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # No connection pooling untuk migrations
    )

    # ========================================================================
    # RUN MIGRATIONS
    # ========================================================================
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # ====================================================================
            # MIGRATION OPTIONS
            # ====================================================================
            # compare_type: Detect column type changes
            # Set True untuk auto-detect type changes
            compare_type=True,
            
            # compare_server_default: Detect server default changes
            compare_server_default=True,
            
            # include_schemas: Include all schemas in migration
            include_schemas=False,
            
            # render_as_batch: Use batch mode untuk SQLite compatibility
            # Set True jika menggunakan SQLite
            render_as_batch=False,
        )

        with context.begin_transaction():
            context.run_migrations()


# ============================================================================
# EXECUTION
# ============================================================================
if context.is_offline_mode():
    """
    Offline mode: Generate SQL scripts without database connection
    """
    run_migrations_offline()
else:
    """
    Online mode: Apply migrations to database
    """
    run_migrations_online()


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
Common Alembic Commands:

1. CREATE MIGRATION:
   # Auto-generate dari model changes
   alembic revision --autogenerate -m "Add users table"
   
   # Manual migration (empty template)
   alembic revision -m "Manual migration"

2. APPLY MIGRATIONS:
   # Upgrade to latest
   alembic upgrade head
   
   # Upgrade to specific revision
   alembic upgrade <revision_id>
   
   # Upgrade one step
   alembic upgrade +1

3. ROLLBACK MIGRATIONS:
   # Downgrade one step
   alembic downgrade -1
   
   # Downgrade to specific revision
   alembic downgrade <revision_id>
   
   # Downgrade all
   alembic downgrade base

4. CHECK STATUS:
   # Current revision
   alembic current
   
   # Migration history
   alembic history
   
   # Verbose history
   alembic history --verbose

5. GENERATE SQL (offline mode):
   # Generate upgrade SQL
   alembic upgrade head --sql > upgrade.sql
   
   # Generate downgrade SQL
   alembic downgrade -1 --sql > downgrade.sql

6. STAMP DATABASE:
   # Mark database as current (without running migrations)
   alembic stamp head
   
   # Useful when database is manually updated

Migration File Structure:
    
    alembic/
    ├── versions/
    │   ├── 001_initial_migration.py
    │   ├── 002_add_posts_table.py
    │   └── 003_add_user_avatar.py
    └── env.py

Each migration file contains:
    - revision: Unique ID
    - down_revision: Previous revision ID
    - upgrade(): Function untuk apply changes
    - downgrade(): Function untuk revert changes

Example Migration File:
    
    def upgrade():
        op.create_table(
            'posts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('content', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    
    def downgrade():
        op.drop_table('posts')

Best Practices:

1. ALWAYS review auto-generated migrations before applying
2. Test migrations in development first
3. Backup database before running migrations in production
4. Use descriptive migration messages
5. Keep migrations small and focused
6. Don't modify old migrations (create new ones)
7. Version control your migrations
8. Document complex migrations

Common Issues:

1. "Target database is not up to date":
   - Database schema doesn't match migration history
   - Solution: alembic stamp head (if schema is correct)

2. "Can't locate revision":
   - Migration file missing or renamed
   - Solution: Check alembic/versions/ directory

3. "Multiple heads":
   - Conflicting migration branches
   - Solution: alembic merge heads

4. Import errors:
   - Models not imported in app/db/base.py
   - Solution: Import all models in base.py
"""