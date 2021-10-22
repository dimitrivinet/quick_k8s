# pylint: disable=too-few-public-methods
from sqlalchemy.orm import registry
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

mapper_registry = registry()
Base = mapper_registry.generate_base()


class User(Base):  # type: ignore
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    hashed_password = Column(String(256))
    disabled = Column(Boolean())
    role = Column(String(50), ForeignKey("roles.name"))


class Role(Base):  # type: ignore
    """Role model."""

    __tablename__ = "roles"

    name = Column(String(50), primary_key=True)
