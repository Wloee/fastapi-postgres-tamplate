"""
============================================================================
SECURITY MODULE
============================================================================
Module ini berisi fungsi-fungsi untuk keamanan aplikasi:
- Password hashing dan verification
- JWT token creation dan validation
- Authentication utilities

Dependencies:
    - passlib: untuk password hashing
    - python-jose: untuk JWT tokens
============================================================================
"""

from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


# ============================================================================
# PASSWORD HASHING CONTEXT
# ============================================================================
# Menggunakan bcrypt algorithm untuk hashing password
# bcrypt secara otomatis menambahkan salt untuk keamanan
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# PASSWORD FUNCTIONS
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify apakah plain password cocok dengan hashed password.
    
    Args:
        plain_password (str): Password yang diinput user (plaintext)
        hashed_password (str): Password yang sudah di-hash di database
        
    Returns:
        bool: True jika password cocok, False jika tidak
        
    Example:
        >>> hashed = get_password_hash("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash password menggunakan bcrypt.
    Function ini akan menghasilkan hash yang berbeda untuk password yang sama
    karena bcrypt otomatis menambahkan random salt.
    
    Args:
        password (str): Password plaintext yang akan di-hash
        
    Returns:
        str: Password yang sudah di-hash
        
    Example:
        >>> hashed = get_password_hash("mypassword123")
        >>> print(hashed)
        $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7gjtkJ3Ve6
        
    Note:
        - Jangan pernah simpan password plaintext di database
        - Selalu hash password sebelum menyimpan
        - Hash yang sama dari password yang sama akan berbeda karena salt
    """
    return pwd_context.hash(password)


# ============================================================================
# JWT TOKEN FUNCTIONS
# ============================================================================

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: timedelta | None = None
) -> str:
    """
    Membuat JWT access token.
    
    Token berisi:
    - sub: subject (biasanya user_id atau email)
    - exp: expiration time
    
    Args:
        subject (str | Any): Subject dari token (user_id atau identifier lain)
        expires_delta (timedelta, optional): Custom expiration time.
            Jika None, akan menggunakan ACCESS_TOKEN_EXPIRE_MINUTES dari settings.
            
    Returns:
        str: JWT token yang sudah di-encode
        
    Example:
        >>> token = create_access_token(subject="user@example.com")
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        
        >>> # Custom expiration (1 jam)
        >>> token = create_access_token(
        ...     subject="user@example.com",
        ...     expires_delta=timedelta(hours=1)
        ... )
        
    Note:
        Token ini harus dikirim di header Authorization:
        Authorization: Bearer <token>
    """
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Buat payload untuk JWT
    to_encode = {
        "exp": expire,      # Expiration time
        "sub": str(subject) # Subject (user identifier)
    }
    
    # Encode JWT dengan secret key dan algorithm dari settings
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode dan validate JWT token.
    
    Args:
        token (str): JWT token yang akan di-decode
        
    Returns:
        dict | None: Payload dari token jika valid, None jika invalid
        
    Example:
        >>> token = create_access_token(subject="user@example.com")
        >>> payload = decode_access_token(token)
        >>> print(payload)
        {'exp': 1234567890, 'sub': 'user@example.com'}
        
    Note:
        Function ini akan return None jika:
        - Token sudah expired
        - Token signature tidak valid
        - Token format salah
    """
    try:
        # Decode token dengan secret key dan algorithm
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.JWTError:
        # Token invalid, expired, atau error lainnya
        return None


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_password_reset_token(email: str) -> str:
    """
    Generate token untuk password reset.
    Token ini biasanya dikirim via email dan memiliki expiration lebih pendek.
    
    Args:
        email (str): Email user yang request reset password
        
    Returns:
        str: JWT token untuk password reset
        
    Example:
        >>> token = generate_password_reset_token("user@example.com")
        >>> # Kirim token ini via email ke user
    """
    # Password reset token berlaku 1 jam
    delta = timedelta(hours=1)
    return create_access_token(subject=email, expires_delta=delta)


def verify_password_reset_token(token: str) -> str | None:
    """
    Verify token untuk password reset dan return email.
    
    Args:
        token (str): Token yang diterima dari email
        
    Returns:
        str | None: Email user jika token valid, None jika invalid
        
    Example:
        >>> token = generate_password_reset_token("user@example.com")
        >>> email = verify_password_reset_token(token)
        >>> print(email)
        user@example.com
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")
    return None


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
if __name__ == "__main__":
    """
    Contoh penggunaan security functions.
    Jalankan file ini untuk test:
        python -m app.core.security
    """
    print("=" * 70)
    print("SECURITY MODULE EXAMPLES")
    print("=" * 70)
    
    # Example 1: Password hashing
    print("\n1. PASSWORD HASHING")
    password = "mySecurePassword123"
    hashed = get_password_hash(password)
    print(f"Original: {password}")
    print(f"Hashed: {hashed}")
    print(f"Verification: {verify_password(password, hashed)}")
    print(f"Wrong password: {verify_password('wrongpass', hashed)}")
    
    # Example 2: JWT Token
    print("\n2. JWT TOKEN")
    token = create_access_token(subject="user@example.com")
    print(f"Token: {token[:50]}...")
    payload = decode_access_token(token)
    print(f"Decoded: {payload}")
    
    print("=" * 70)