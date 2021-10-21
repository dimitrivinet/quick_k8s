# pylint: disable=missing-docstring
from fastapi import Depends, FastAPI

from app import routers
from app.utils import auth


app = FastAPI()


@app.get("/")
async def home():

    return {"msg": "Welcome"}


@app.get("/users/me", response_model=auth.User, tags=["Test"])
async def read_users_me(
    current_user: auth.User = Depends(auth.get_current_active_user),
):
    return current_user


app.include_router(routers.router)
