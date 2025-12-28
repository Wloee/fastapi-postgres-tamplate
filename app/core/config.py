"""
============================================================================
CONFIGURATION MODULE
============================================================================
Module ini berisi semua konfigurasi aplikasi yang diambil dari environment
variables. Menggunakan Pydantic Settings untuk validasi otomatis.

Cara penggunaan:
    from app.core.config import settings
    
    print(settings.PROJECT_NAME)
    print(settings.DATABASE_URL)
============================================================================
"""

from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings class untuk manage semua konfigurasi aplikasi.
    
    Pydantic akan otomatis membaca environment variables dari:
    1. System environment variables
    2. .env file (jika ada)
    
    Attributes:
        PROJECT_NAME (str): Nama project
        API_V1_STR (str): Prefix untuk API v1 endpoints
        SECRET_KEY (str): Secret key untuk JWT dan security
        ALGORITHM (str): Algorithm untuk JWT encoding
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Durasi token dalam menit
        BACKEND_CORS_ORIGINS (List): List of allowed origins untuk CORS
        
    Database Attributes:
        POSTGRES_SERVER (str): Host database server
        POSTGRES_USER (str): Username database
        POSTGRES_PASSWORD (str): Password database
        POSTGRES_DB (str): Nama database
        POSTGRES_PORT (int): Port database
        DATABASE_URL (str): Full connection string (auto-generated)
    """
    
    # ========================================================================
    # APPLICATION SETTINGS
    # ========================================================================
    PROJECT_NAME: str = "FastAPI PostgreSQL Project"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # ========================================================================
    # SECURITY SETTINGS
    # ========================================================================
    # Secret key harus panjang dan random. Generate dengan:
    # openssl rand -hex 32
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    
    # Token expiration: 43200 minutes = 30 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    
    # ========================================================================
    # CORS (Cross-Origin Resource Sharing) SETTINGS
    # ========================================================================
    # List of origins yang diizinkan untuk akses API
    # Contoh: ["http://localhost:3000", "https://yourdomain.com"]
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """
        Validator untuk CORS origins.
        Jika input berupa string, akan di-split menjadi list.
        
        Args:
            v: String atau List of strings
            
        Returns:
            List of valid origins
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # ========================================================================
    # DATABASE SETTINGS
    # ========================================================================
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    
    # Database URL akan di-generate otomatis
    DATABASE_URL: str | None = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info) -> str:
        """
        Generate DATABASE_URL dari komponen-komponen database.
        Jika DATABASE_URL sudah di-set di environment, gunakan itu.
        Jika tidak, generate dari POSTGRES_* variables.
        
        Args:
            v: DATABASE_URL dari environment (optional)
            info: ValidationInfo yang berisi field values lainnya
            
        Returns:
            str: Complete PostgreSQL connection string
            
        Example:
            postgresql://user:pass@localhost:5432/dbname
        """
        if isinstance(v, str):
            return v
        
        # Generate connection string dari komponen
        return (
            f"postgresql://{info.data.get('POSTGRES_USER')}:"
            f"{info.data.get('POSTGRES_PASSWORD')}@"
            f"{info.data.get('POSTGRES_SERVER')}:"
            f"{info.data.get('POSTGRES_PORT')}/"
            f"{info.data.get('POSTGRES_DB')}"
        )
    
    # ========================================================================
    # FIRST SUPERUSER
    # ========================================================================
    # User pertama yang akan dibuat saat inisialisasi database
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "changethis"
    
    class Config:
        """
        Konfigurasi untuk Pydantic Settings.
        
        - case_sensitive: Environment variables case-sensitive
        - env_file: File untuk load environment variables
        """
        case_sensitive = True
        env_file = ".env"


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
# Instance tunggal dari Settings yang akan digunakan di seluruh aplikasi
# Import ini di module lain:
#   from app.core.config import settings
settings = Settings()


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
if __name__ == "__main__":
    """
    Contoh penggunaan settings.
    Jalankan file ini untuk test konfigurasi:
        python -m app.core.config
    """
    print("=" * 70)
    print("CONFIGURATION SETTINGS")
    print("=" * 70)
    print(f"Project Name: {settings.PROJECT_NAME}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"API Prefix: {settings.API_V1_STR}")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"CORS Origins: {settings.BACKEND_CORS_ORIGINS}")
    print("=" * 70)