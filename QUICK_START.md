# 🚀 Quick Start Guide

Panduan cepat untuk memulai project FastAPI + PostgreSQL ini dalam 5 menit!

## 📋 Prerequisites

- Python 3.10 atau lebih tinggi
- PostgreSQL 12 atau lebih tinggi
- pip atau poetry

## ⚡ 5-Minute Setup

### 1️⃣ Clone & Setup Virtual Environment

```bash
# Clone repository
git clone <repository-url>
cd fastapi-postgres-project

# Buat virtual environment
python -m venv venv

# Aktivasi virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Setup Database

```bash
# Login ke PostgreSQL
psql -U postgres

# Jalankan SQL commands ini:
CREATE DATABASE fastapi_db;
CREATE USER fastapi_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;
\q
```

### 4️⃣ Configure Environment

```bash
# Copy .env.example ke .env
cp .env.example .env

# Edit .env file (gunakan text editor favorit Anda)
nano .env
# atau
code .env
```

Minimal configuration yang perlu diubah:
```env
POSTGRES_PASSWORD=your_password_here
SECRET_KEY=generate-random-32-character-key
```

**Generate SECRET_KEY:**
```bash
# Windows (PowerShell):
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})

# Linux/Mac:
openssl rand -hex 32
```

### 5️⃣ Run Application

```bash
# Option 1: Using run.py
python run.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --reload
```

✅ **Application is now running!**
- Main URL: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## 🎯 First Steps

### 1. Access API Documentation

Buka browser dan kunjungi: http://localhost:8000/docs

Anda akan melihat interactive API documentation (Swagger UI).

### 2. Login dengan Default Admin

Default credentials (dari FIRST_SUPERUSER di .env):
- **Email**: admin@example.com
- **Password**: changethis

### 3. Test API dengan Swagger UI

#### Login:
1. Klik endpoint `POST /api/v1/auth/login`
2. Klik "Try it out"
3. Masukkan credentials:
   ```json
   {
     "username": "admin@example.com",
     "password": "changethis"
   }
   ```
4. Klik "Execute"
5. Copy `access_token` dari response

#### Authorize:
1. Klik tombol "Authorize" di atas (🔒)
2. Paste token dengan format: `Bearer <your_token>`
3. Klik "Authorize"

#### Test Protected Endpoint:
1. Klik `GET /api/v1/users/me`
2. Klik "Try it out" → "Execute"
3. Anda akan melihat data user Anda!

### 4. Test dengan cURL (Optional)

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis"

# Simpan token dari response, lalu:
# Get current user (ganti <TOKEN> dengan token Anda)
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <TOKEN>"
```

## 🗄️ Database Migrations

### Initialize Migrations (sudah dilakukan)

```bash
alembic init alembic
```

### Create First Migration

```bash
# Generate migration dari models
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Future Model Changes

Setiap kali mengubah models:

```bash
# 1. Generate migration
alembic revision --autogenerate -m "Description of changes"

# 2. Review generated file di alembic/versions/

# 3. Apply migration
alembic upgrade head
```

## 📝 Common Tasks

### Create New User

```bash
# Via API (need to be logged in as admin)
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123",
    "full_name": "New User",
    "is_active": true,
    "is_superuser": false
  }'
```

### Update Current User

```bash
curl -X PUT "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name"
  }'
```

### Get All Users (Admin Only)

```bash
curl -X GET "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer <TOKEN>"
```

## 🔧 Development Workflow

### 1. Add New Model

```python
# app/models/post.py
from sqlalchemy import Column, String, Text
from app.db.base_class import Base

class Post(Base):
    title = Column(String(200), nullable=False)
    content = Column(Text)
```

### 2. Import Model in base.py

```python
# app/db/base.py
from app.models.user import User
from app.models.post import Post  # Add this
```

### 3. Create Schemas

```python
# app/schemas/post.py
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str

class Post(PostCreate):
    id: int
    
    class Config:
        from_attributes = True
```

### 4. Create CRUD

```python
# app/crud/crud_post.py
from app.crud.base import CRUDBase
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate

class CRUDPost(CRUDBase[Post, PostCreate, PostUpdate]):
    pass

post = CRUDPost(Post)
```

### 5. Create Endpoints

```python
# app/api/v1/endpoints/posts.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.crud.crud_post import post as crud_post
from app.schemas import post as schemas

router = APIRouter()

@router.get("/posts")
def get_posts(db: Session = Depends(deps.get_db)):
    posts = crud_post.get_multi(db)
    return posts
```

### 6. Register Router

```python
# app/main.py
from app.api.v1.endpoints import users, posts

app.include_router(posts.router, prefix=settings.API_V1_STR, tags=["posts"])
```

### 7. Run Migration

```bash
alembic revision --autogenerate -m "Add posts table"
alembic upgrade head
```

## 🐛 Troubleshooting

### Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in `.env` file
- Check POSTGRES_SERVER, POSTGRES_PORT

### Import Errors

```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
- Make sure you're in project root directory
- Virtual environment is activated
- All dependencies installed: `pip install -r requirements.txt`

### Migration Errors

```
Target database is not up to date
```

**Solution:**
```bash
alembic stamp head
alembic upgrade head
```

### Token Expired

**Solution:**
Login lagi untuk mendapatkan token baru. Token expired sesuai ACCESS_TOKEN_EXPIRE_MINUTES di .env (default: 30 hari).

## 📚 Next Steps

1. **Baca README.md** untuk dokumentasi lengkap
2. **Explore code** dengan banyak komentar di setiap file
3. **Add features** sesuai kebutuhan project Anda
4. **Write tests** untuk code baru
5. **Deploy** ke production saat siap

## 🎓 Learning Resources

### FastAPI
- [Official Documentation](https://fastapi.tiangolo.com/)
- [Tutorial](https://fastapi.tiangolo.com/tutorial/)

### SQLAlchemy
- [Documentation](https://docs.sqlalchemy.org/)
- [ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)

### PostgreSQL
- [Official Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)

## 💡 Tips

1. **Always activate virtual environment** sebelum coding
2. **Use .env file** untuk sensitive data, jangan commit ke git
3. **Generate strong SECRET_KEY** untuk production
4. **Use Alembic migrations** instead of manual schema changes
5. **Write tests** untuk features baru
6. **Check logs** jika ada error
7. **Use Swagger UI** untuk test API dengan mudah

## ⚠️ Important Notes

- ❌ **JANGAN** commit file `.env` ke git (sudah di .gitignore)
- ✅ **SELALU** backup database sebelum migration di production
- ✅ **GUNAKAN** virtual environment untuk isolasi dependencies
- ✅ **GANTI** default password dan SECRET_KEY di production
- ✅ **TEST** di development sebelum deploy ke production

---

**Happy Coding! 🚀**

Jika ada pertanyaan atau issues, silakan buat issue di repository atau hubungi maintainer.