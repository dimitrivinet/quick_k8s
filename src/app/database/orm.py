"""
The tables' definitions.
"""

# pylint: disable=too-few-public-methods
from sqlalchemy.orm import registry
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime

mapper_registry = registry()
Base = mapper_registry.generate_base()


class User(Base):  # type: ignore
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(100), unique=True)
    email = Column(String(100))
    hashed_password = Column(String(256))
    disabled = Column(Boolean())
    role = Column(Integer, ForeignKey("roles.id"))

    def dict(self) -> dict:
        """Returns a dict representation of the user."""

        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "disabled": self.disabled,
            "role": self.role,
        }

    def __repr__(self):
        return (
            f"User(id={self.id}, "
            f"first_name={self.first_name}, "
            f"last_name={self.last_name}, "
            f"username={self.username}, "
            f"email={self.email}, "
            f"hashed_password={self.hashed_password}, "
            f"disabled={self.disabled}, "
            f"role={self.role})"
        )


class Role(Base):  # type: ignore
    """Role model."""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))


class Resource(Base):  # type: ignore
    """Kubernetes resource model."""

    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(Integer, ForeignKey("users.id"))
    name = Column(String(50))
    type = Column(String(50))
    created_timestamp = Column(DateTime(timezone=False))
    modified_timestamp = Column(DateTime(timezone=False), nullable=True)
    deleted_timestamp = Column(DateTime(timezone=False), nullable=True)
