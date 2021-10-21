# pylint: disable=too-few-public-methods
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyQuery, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from app import dummy_db

# # to get a string like this run:
# # openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
api_key_scheme = APIKeyQuery(name="api_key")

class Token(BaseModel):
    """Token class."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Class for data associated to token."""

    username: Optional[str] = None


class User(BaseModel):
    """User class."""

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False


class UserInDB(User):
    """Representation of user in database."""

    hashed_password: str

def verify_password(plain_password, hashed_password):
    """Verify provided password against stored password."""

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Get hash from plain password."""

    return pwd_context.hash(password)


def get_user(db, username: Optional[str]) -> Optional[UserInDB]:
    """Get user data from username."""

    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

    return None


def authenticate_user(fake_db, username: str, password: str):
    """Authenticate user from provided username and passord."""

    user = get_user(fake_db, username)
    if user is None:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create access token at login."""

    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token."""

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
        raise credentials_exception from JWTError

    user = get_user(dummy_db.fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Check if current user is active (not disabled)."""

    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
