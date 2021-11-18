# pylint: disable=too-few-public-methods
from enum import Enum
import os
from datetime import datetime, timedelta
from typing import Literal, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyQuery, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, validator  # pylint: disable=no-name-in-module

from app import database
from app.config import cfg


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
api_key_scheme = APIKeyQuery(name="api_key")


class Role(Enum):
    """Roles class."""

    ADMIN = 1
    NEW = 2
    EXPERIENCED = 3
    TRUSTED = 4


class Token(BaseModel):
    """Token class."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Class for data associated to token."""

    username: Optional[str] = None


class User(BaseModel):
    """User class."""

    first_name: str
    last_name: str
    username: str
    email: str
    disabled: bool
    role: str

    @validator("role")
    def validate_role(cls, v):  # pylint: disable=no-self-argument,no-self-use
        """Check if role is an allowed Role."""

        role_names = [role.name for role in Role]

        if v.upper() in role_names:
            return v.upper()

        raise ValueError(f"Role {v} is not and allowed Role.")


class UserInDB(User):
    """Representation of user in database. Password is hashed at init."""

    hashed_password: str


class Password(BaseModel):
    """Representation of a password."""

    password: str
    is_hashed: bool


def verify_password(plain_password, hashed_password):
    """Verify provided password against stored password."""

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Get hash from plain password."""

    return pwd_context.hash(password)


def get_user(username: Optional[str]) -> Optional[UserInDB]:
    """Get user data from username."""

    user = database.users.get_user(username)
    if user is None:
        return None

    user_dict = user.dict()
    user_dict["role"] = Role(user_dict["role"]).name

    return UserInDB(**user_dict)


def authenticate_user(username: str, password: str) -> Union[User, Literal[False]]:
    """Authenticate user from provided username and passord.
    Returns False if user doesn't exist or the password is incorrect."""

    user = get_user(username)

    if user is None:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return User(**user.dict())


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create access token at login."""

    to_encode = data.copy()

    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, cfg.SECRET_KEY, algorithm=cfg.ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from token."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, cfg.SECRET_KEY, algorithms=[cfg.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception from JWTError

    user = get_user(username=token_data.username)

    if user is None:
        raise credentials_exception

    return User(**user.dict())


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    """Check if current user is active (not disabled)."""

    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


async def current_user_is_admin(
    current_user: UserInDB = Depends(get_current_active_user),
):
    """Checks if current user is active and has admin role."""

    print(current_user.role, Role.ADMIN.name)
    if current_user.role != Role.ADMIN.name:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    return current_user
