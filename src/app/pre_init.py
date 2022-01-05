import logging

import sqlalchemy

from app import database
from app.config import cfg
from app.utils import auth


def pre_init():
    logger = logging.getLogger("uvicorn.error")

    # setup database engine and tables if first run
    database.utils.setup_engine(cfg.DATABASE_URL, echo=False)
    database.utils.create_tables()
    try:
        database.roles.populate_roles_table()
    except sqlalchemy.exc.IntegrityError:
        logger.info("Kept roles table from previous init.")

    # Set default admin profile for first run
    hashed_password = auth.get_password_hash(cfg.DEFAULT_ADMIN_PASSWORD)

    default_admin = database.orm.User(
        first_name="admin",
        last_name="admin",
        username="admin",
        email=cfg.DEFAULT_ADMIN_EMAIL,
        hashed_password=hashed_password,
        disabled=False,
        role=auth.Role.ADMIN.value,
    )

    logger.info("Adding default admin profile.")
    try:
        database.users.add_user(default_admin)
        logger.info("Added default admin profile.")
    except sqlalchemy.exc.IntegrityError:
        logger.info("Default admin was already inserted.")

    logger.info("Setup database.")
