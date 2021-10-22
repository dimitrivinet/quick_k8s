# pylint: disable=missing-docstring
import os
import logging

from fastapi import Depends, FastAPI

from app import routers, database
from app.utils import auth

logger = logging.getLogger("uvicorn.error")

DATABASE_URL = os.getenv("DATABASE_URL", "")
database.setup_engine(DATABASE_URL, echo=True)
database.create_tables()
logger.info("Setup database.")


app = FastAPI()

app.include_router(routers.router)


@app.get("/")
async def home():

    return {"msg": "Welcome"}


@app.get("/users/me", response_model=auth.User, tags=["Test"])
async def read_users_me(
    current_user: auth.User = Depends(auth.get_current_active_user),
):
    return current_user
