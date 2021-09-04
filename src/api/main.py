import os
from datetime import datetime, timedelta
from typing import Iterator, Optional

import dotenv
import yaml
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.security import (APIKeyQuery, OAuth2PasswordBearer,
                              OAuth2PasswordRequestForm)
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from . import dummy_db, k8s

dotenv.load_dotenv()

# # to get a string like this run:
# # openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TARGET_NAMESPACE = os.getenv("TARGET_NAMESPACE")


ACCESS_TOKEN_EXPIRE_MINUTES = 144


openapi_tags_metadata = [
    {"name": "Base", "description": "Base endpoints"},
    {"name": "k8s",  "description": "Kubernetes"},
    {"name": "Auth", "description": "Authentification relevant endpoints"},
    {"name": "Test", "description": "Test endpoints"},
]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_key_scheme = APIKeyQuery(name="api_key")

app = FastAPI(openapi_tags=openapi_tags_metadata)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    user = get_user(dummy_db.fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/", tags=["Base"])
async def home():
    return {"msg": "Welcome"}


@app.post("/token", response_model=Token, tags=["Auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(dummy_db.fake_users_db,
                             form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/hash", tags=["Auth"])
async def read_token(password: str):
    hashed_password = get_password_hash(password)
    return {"hashed_password": hashed_password}


@app.get("/api_key_test", tags=["Test"])
async def api_key_test(key: str = Depends(api_key_scheme)):
    return {"key": key}


@app.get("/users/me", response_model=User, tags=["Test"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.post("/k8s/deployments", tags=["k8s"])
async def create_deployment(yaml_file: UploadFile = File(...),
                            namespace_exists: None = Depends(
                                k8s.check_namespace(TARGET_NAMESPACE)),
                            current_user: User = Depends(
                                get_current_active_user)):
    filename = yaml_file.filename

    yamls_as_dicts: Iterator = yaml.safe_load_all(yaml_file.file)
    yamls_as_dicts = [yaml_as_dict for yaml_as_dict in yamls_as_dicts]

    for doc in yamls_as_dicts:
        validation_result = k8s.validate(doc, TARGET_NAMESPACE)

        if not validation_result.result:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=validation_result.reason)

    deployed = []
    for doc in yamls_as_dicts:
        deployment_result = k8s.deploy(doc, TARGET_NAMESPACE)

        if not deployment_result.result:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=deployment_result.reason)

        deployed.append(deployment_result.info)

    return {"deployed": deployed, "filename": filename}
