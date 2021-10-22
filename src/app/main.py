# pylint: disable=missing-docstring
import os
import logging

from fastapi import FastAPI

from app import routers, database

logger = logging.getLogger("uvicorn.error")

DATABASE_URL = os.getenv("DATABASE_URL", "")
database.setup_engine(DATABASE_URL, echo=False)
database.create_tables()
if not database.roles.populate_roles_table():
    logger.info("Kept roles table from previous init.")
logger.info("Setup database.")


app = FastAPI()

app.include_router(routers.router)


@app.get("/")
async def home():

    return {"msg": "Welcome to the quick_k8s API. More info @ /docs"}
