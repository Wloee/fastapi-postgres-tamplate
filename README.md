# FastAPI + PostgreSQL Template Project

Template project untuk membangun REST API menggunakan **FastAPI** dan **PostgreSQL** dengan struktur code yang clean, reusable, dan mudah dikembangkan.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database Migrations](#database-migrations)
- [Testing](#testing)
- [Deployment](#deployment)
- [Best Practices](#best-practices)

## ✨ Features

- ✅ **FastAPI Framework** - Modern, fast, dan dengan automatic API documentation
- ✅ **PostgreSQL Database** - Reliable relational database
- ✅ **SQLAlchemy ORM** - Powerful ORM untuk Python
- ✅ **Alembic Migrations** - Database version control
- ✅ **Pydantic Validation** - Data validation dengan Python type hints
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **CRUD Operations** - Reusable CRUD base class
- ✅ **User Management** - Complete user management system
- ✅ **Role-based Access Control** - Admin dan user permissions
- ✅ **Password Hashing** - Secure password dengan bcrypt
- ✅ **CORS Support** - Configured CORS middleware
- ✅ **Environment Variables** - Secure configuration management
- ✅ **Code Documentation** - Extensive comments dan docstrings

## 🛠 Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 12+
- **ORM**: SQLAlchemy 2.0+
- **Migration**: Alembic 1.12+
- **Validation**: Pydantic 2.5+
- **Security**: python-jose, passlib
- **Server**: Uvicorn

## 📁 Project Structure

```
fastapi-postgres-project/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point aplikasi
│   │
│   ├── api/                    # API layer
│   │   ├── __init__.py
│   │   ├── deps.py            # Dependencies (auth, db session)
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── users.py   # User endpoints
│   │
│   ├── core/                   # Core configurations
│   │   ├── __init__.py
│   │   ├── config.py          # Settings
│   │   └── security.py        # Security utilities
│   │
│   ├── db/                     # Database setup
│   │   ├── __init__.py
│   │   ├── base.py            # Import all models
│   │   ├── session.py         # DB session
│   │   └── base_class.py      # Base model class
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── user.py            # User model
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   └── user.py            # User schemas
│   │
│   ├── crud/                   # CRUD operations
│   │   ├── __init__.py
│   │   ├── base.py            # Base CRUD
│   │   └── crud_user.py       # User CRUD
│   │
│   └── services/               # Business logic (optional)
│       └── __init__.py
│
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/                      # Tests
│   └── __init__.py
│
├── .env                        # Environment variables (don't commit!)
├── .env.example               # Environment template
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

## 🚀 Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip atau poetry

### Steps

1. **Clone repository**
```bash
git clone <repository-url>
cd fastapi-postgres-project
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup PostgreSQL database**
```bash
# Login ke PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE fastapi_db;

# Create user (optional)
CREATE USER fastapi_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;
```

5. **Setup environment variables**
```bash
# Copy .env.example ke .env
cp .env.example .env

# Edit .env dengan text editor
# Update database credentials dan SECRET_KEY
```

## ⚙️ Configuration

Edit file `.env` dengan konfigurasi Anda:

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=fastapi_db
POSTGRES_PORT=5432

# Security
SECRET_KEY=your-super-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# First superuser
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis
```

**PENTING**: Generate SECRET_KEY yang kuat:
```bash
openssl rand -hex 32
```

## 🏃 Running the Application

### Development Mode

```bash
# Dengan uvicorn (recommended)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Atau dengan python
python -m app.main
```

Application akan berjalan di: `http://localhost:8000`

### Production Mode

```bash
# Dengan gunicorn (untuk production)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 API Documentation

Setelah aplikasi running, akses dokumentasi:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### Available Endpoints

#### Authentication
- `POST /api/v1/auth/login` - Login to get access token

#### Users
- `GET /api/v1/users/me` - Get current user (authenticated)
- `PUT /api/v1/users/me` - Update current user (authenticated)
- `GET /api/v1/users` - List all users (admin only)
- `POST /api/v1/users` - Create new user (admin only)
- `GET /api/v1/users/{id}` - Get user by ID (admin only)
- `PUT /api/v1/users/{id}` - Update user (admin only)
- `DELETE /api/v1/users/{id}` - Delete user (admin only)

### Quick Start Guide

1. **Login untuk mendapatkan token**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

2. **Gunakan token untuk akses protected endpoints**
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <your_token>"
```

## 🗄️ Database Migrations

### Initialize Alembic

```bash
# Sudah di-setup, tapi jika perlu init ulang:
alembic init alembic
```

### Create Migration

```bash
# Auto-generate migration dari model changes
alembic revision --autogenerate -m "Description of changes"

# Contoh: Tambah table posts
alembic revision --autogenerate -m "Add posts table"
```

### Run Migrations

```bash
# Upgrade ke latest version
alembic upgrade head

# Upgrade ke specific revision
alembic upgrade <revision_id>

# Downgrade satu step
alembic downgrade -1

# Downgrade ke specific revision
alembic downgrade <revision_id>
```

### Check Migration Status

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_users.py

# Run with verbose output
pytest -v
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Test fixtures
├── test_users.py         # User endpoint tests
└── test_auth.py          # Authentication tests
```

## 🚀 Deployment

### Using Docker

1. **Create Dockerfile**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Create docker-compose.yml**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_SERVER=db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=fastapi_db
    depends_on:
      - db

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=fastapi_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

3. **Run with Docker Compose**
```bash
docker-compose up -d
```

### Deploy to Cloud

#### Heroku
```bash
# Install Heroku CLI
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

#### DigitalOcean / AWS / GCP
- Setup server dengan Python 3.10+
- Install PostgreSQL
- Clone repository
- Setup environment variables
- Run dengan gunicorn
- Configure nginx as reverse proxy

## 📝 Best Practices

### Code Organization

1. **Separation of Concerns**
   - Models: Database structure
   - Schemas: API contracts
   - CRUD: Database operations
   - Services: Business logic
   - Endpoints: HTTP handlers

2. **Dependency Injection**
   - Use `Depends()` untuk reusable logic
   - Database session management
   - Authentication checks

3. **Error Handling**
   - Consistent error responses
   - HTTP status codes
   - Validation errors

### Security

1. **Never commit `.env` file**
2. **Use strong SECRET_KEY** (min 32 characters)
3. **Hash passwords** (bcrypt)
4. **Validate all inputs** (Pydantic)
5. **Use HTTPS** in production
6. **Implement rate limiting**
7. **Keep dependencies updated**

### Database

1. **Use migrations** untuk schema changes
2. **Add indexes** pada frequently queried columns
3. **Use soft delete** instead of hard delete
4. **Implement pagination** untuk large datasets
5. **Connection pooling** untuk performance

### Development Workflow

1. **Create feature branch**
```bash
git checkout -b feature/new-feature
```

2. **Make changes dengan tests**
```bash
# Write code
# Write tests
pytest
```

3. **Create migration jika ada model changes**
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

4. **Commit dan push**
```bash
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

5. **Create pull request**

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Happy Coding! 🚀**