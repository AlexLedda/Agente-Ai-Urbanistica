from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from backend.core.security import ALGORITHM, SECRET_KEY
from backend.models.user import TokenData, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Mock DB - duplicato per evitare circular imports per ora.
# TODO: Spostare in un modulo dedicato
users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": "", # Non serve per verifica token, solo username
        "disabled": False
    }
}

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user_dict = users_db.get(token_data.username)
    if user_dict is None:
        raise credentials_exception
        
    user = User(**user_dict)
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
