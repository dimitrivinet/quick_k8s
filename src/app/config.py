import os
from typing import NamedTuple

DATABASE_URL = os.getenv("DATABASE_URL", "")

# # to get a string like this run:
# # openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY", "")
# Python-JOSE algorithm
ALGORITHM = os.getenv("ALGORITHM", "")

# Namespace where applications will be deployed
TARGET_NAMESPACE = os.getenv("TARGET_NAMESPACE", "")


class Config(NamedTuple):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    TARGET_NAMESPACE: str


cfg = Config(
    DATABASE_URL=DATABASE_URL,
    SECRET_KEY=SECRET_KEY,
    ALGORITHM=ALGORITHM,
    TARGET_NAMESPACE=TARGET_NAMESPACE,
)
