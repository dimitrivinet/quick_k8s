import os
import sys


def check_config_values(config: dict):
    for conf in config:
        if config[conf] == "":
            sys.exit(f"Value {conf} was not set but is necessary.")


class Config(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


cfg = Config()


cfg.DATABASE_URL = os.getenv("DATABASE_URL", "")

# # to get a string like this run:
# # openssl rand -hex 32
cfg.SECRET_KEY = os.getenv("SECRET_KEY", "")
# Python-JOSE algorithm
cfg.ALGORITHM = os.getenv("ALGORITHM", "")

# Namespace where applications will be deployed
cfg.TARGET_NAMESPACE = os.getenv("TARGET_NAMESPACE", "")

cfg.DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "")
cfg.DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "")

check_config_values(cfg)
