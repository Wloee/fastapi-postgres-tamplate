"""
============================================================================
FASTAPI MAIN APPLICATION
============================================================================
Entry point untuk FastAPI application.

Features:
    - FastAPI instance setup
    - CORS middleware
    - API routers
    - Database initialization
    - Health check endpoint
    - Swagger documentation

Run aplikasi dengan:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    
Atau dengan Python:
    python -m uvicorn app.main:app --reload
============================================================================
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api import deps
from app.api.v1.endpoints import users
from app.core.config import settings
from app.crud.crud_user import user as crud_user
from app.schemas.user import UserCreate


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="""
    FastAPI + PostgreSQL Template Project
    
    ## Features
    * **User Management**: Complete CRUD operations for users
    * **Authentication**: JWT token-based authentication
    * **Authorization**: Role-based access control (superuser)
    * **Database**: PostgreSQL with SQLAlchemy ORM
    * **Migrations**: Alembic for database migrations
    
    ## Authentication
    Most endpoints require authentication. First login to get token:
    1. Use `/api/v1/auth/login` endpoint
    2. Get access token from response
    3. Use token in Authorization header: `Bearer <token>`
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)


# ============================================================================
# CORS MIDDLEWARE
# ============================================================================
"""
Configure CORS (Cross-Origin Resource Sharing).
Memungkinkan frontend dari domain lain untuk akses API.

For production:
    - Specify exact origins
    - Set allow_credentials=True only if needed
    - Limit allowed methods dan headers
"""

# Set CORS origins dari settings
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        # List of allowed origins
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        
        # Allow credentials (cookies, authorization headers)
        allow_credentials=True,
        
        # Allowed HTTP methods
        allow_methods=["*"],  # Or specify: ["GET", "POST", "PUT", "DELETE"]
        
        # Allowed HTTP headers
        allow_headers=["*"],  # Or specify: ["Authorization", "Content-Type"]
    )


# ============================================================================
# INCLUDE ROUTERS
# ============================================================================
"""
Include API routers.
Semua endpoints dari router akan otomatis terdaftar.

Router structure:
    /api/v1/auth/login      - Login endpoint
    /api/v1/users           - User endpoints
    /api/v1/users/me        - Current user endpoints
"""

app.include_router(
    users.router,
    prefix=settings.API_V1_STR,
    tags=["users"]
)

# Tambahkan router lain di sini:
# app.include_router(posts.router, prefix=settings.API_V1_STR, tags=["posts"])
# app.include_router(comments.router, prefix=settings.API_V1_STR, tags=["comments"])


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """
    Root endpoint.
    Simple health check dan info endpoint.
    
    Returns:
        dict: Application info
        
    Example Response:
        {
            "message": "FastAPI + PostgreSQL Template",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api": settings.API_V1_STR
    }


@app.get("/health")
def health_check(db: Session = Depends(deps.get_db)):
    """
    Health check endpoint.
    Check application dan database connection status.
    
    Returns:
        dict: Health status
        
    Example Response:
        {
            "status": "healthy",
            "database": "connected"
        }
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }


# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Event yang dijalankan saat aplikasi start.
    
    Tasks:
        - Initialize database
        - Create first superuser
        - Run migrations (optional)
        - Load initial data (optional)
    """
    print("=" * 70)
    print(f"Starting {settings.PROJECT_NAME}")
    print("=" * 70)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"API URL: {settings.API_V1_STR}")
    print(f"Docs URL: /docs")
    print("=" * 70)
    
    # Initialize database
    from app.db.session import SessionLocal, init_db
    
    # Create tables (for development)
    # For production, use Alembic migrations
    if settings.ENVIRONMENT == "development":
        print("Initializing database...")
        init_db()
    
    # Create first superuser if not exists
    db = SessionLocal()
    try:
        user = crud_user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not user:
            print(f"Creating first superuser: {settings.FIRST_SUPERUSER_EMAIL}")
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name="Admin User",
                is_superuser=True,
                is_active=True
            )
            user = crud_user.create(db, obj_in=user_in)
            print(f"✓ Superuser created successfully")
        else:
            print(f"✓ Superuser already exists: {settings.FIRST_SUPERUSER_EMAIL}")
    except Exception as e:
        print(f"✗ Error creating superuser: {e}")
    finally:
        db.close()
    
    print("=" * 70)
    print("Application started successfully!")
    print("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Event yang dijalankan saat aplikasi shutdown.
    
    Tasks:
        - Close database connections
        - Cleanup resources
        - Save state (if needed)
    """
    print("=" * 70)
    print("Shutting down application...")
    print("=" * 70)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================
"""
Custom exception handlers untuk better error responses.
Bisa ditambahkan sesuai kebutuhan.

Example:
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )
"""


# ============================================================================
# MIDDLEWARE
# ============================================================================
"""
Custom middleware bisa ditambahkan di sini.

Example - Request logging:
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        print(f"{request.method} {request.url}")
        response = await call_next(request)
        return response

Example - Request timing:
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
"""


# ============================================================================
# MAIN (for development)
# ============================================================================

if __name__ == "__main__":
    """
    Run aplikasi dengan:
        python -m app.main
        
    Atau gunakan uvicorn:
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    """
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload saat code berubah (development only)
        log_level="info"
    )


# ============================================================================
# USAGE NOTES
# ============================================================================
"""
Development Workflow:

1. START APPLICATION:
    uvicorn app.main:app --reload
    
    Or with python:
    python -m app.main

2. ACCESS DOCUMENTATION:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - OpenAPI JSON: http://localhost:8000/api/v1/openapi.json

3. TEST ENDPOINTS:
    - Health check: GET http://localhost:8000/health
    - Login: POST http://localhost:8000/api/v1/auth/login
    - Get users: GET http://localhost:8000/api/v1/users/me

4. DEFAULT CREDENTIALS:
    Email: admin@example.com (from FIRST_SUPERUSER_EMAIL)
    Password: changethis (from FIRST_SUPERUSER_PASSWORD)

Production Deployment:

1. Update .env file dengan production values
2. Set ENVIRONMENT=production
3. Use proper SECRET_KEY (generate with: openssl rand -hex 32)
4. Use Alembic migrations instead of init_db()
5. Configure proper CORS origins
6. Use gunicorn atau production ASGI server:
    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

Testing:

1. Run with pytest:
    pytest tests/

2. Test specific file:
    pytest tests/test_users.py

3. With coverage:
    pytest --cov=app tests/
"""