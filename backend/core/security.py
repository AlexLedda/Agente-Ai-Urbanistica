import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from backend.config import settings

# Configurazione JWT
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se la password corrisponde all'hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Genera hash della password."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT di accesso."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
