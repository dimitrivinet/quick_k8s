import os
import sys
from typing import NamedTuple


def check_config_values(config: dict):
    for conf in config:
        if config[conf] == "":
            sys.exit(f"Value {conf} was not set but is necessary.")


class Config(NamedTuple):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # # to get a string like this run:
    # # openssl rand -hex 32
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    # Python-JOSE algorithm
    ALGORITHM: str = os.getenv("ALGORITHM", "")

    # Namespace where applications will be deployed
    TARGET_NAMESPACE: str = os.getenv("TARGET_NAMESPACE", "")

    DEFAULT_ADMIN_EMAIL: str = os.getenv("DEFAULT_ADMIN_EMAIL", "")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "")


cfg = Config()

check_config_values(cfg._asdict())
