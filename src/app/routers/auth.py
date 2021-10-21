# pylint: disable=missing-docstring
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app import dummy_db
from app.utils import auth


ACCESS_TOKEN_EXPIRE_MINUTES = 144

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/token", response_model=auth.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(
        dummy_db.fake_users_db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        # pylint: disable=no-member
        data={"sub": user.username},
        expires_delta=access_token_expires,  # type: ignore
    )
    return auth.Token(access_token=access_token, token_type="bearer")


@router.get("/hash")
async def get_password_hash(password: str):
    hashed_password = auth.get_password_hash(password)
    return {"hashed_password": hashed_password}


@router.get("/api_key_test")
async def api_key_test(key: str = Depends(auth.api_key_scheme)):
    return {"key": key}
