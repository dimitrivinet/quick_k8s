from functools import singledispatch
from typing import Optional

from app.database.orm import User
from app.database.utils import get_session


def add_user(user: User) -> None:
    """Add user to database."""

    session = get_session()
    session.add(user)
    session.commit()


def delete_user(user: User) -> None:
    """Delete user from database."""

    session = get_session()
    session.delete(user)
    session.commit()


@singledispatch
def get_user(username: str) -> Optional[User]:
    """Get user by username."""

    session = get_session()
    user = session.query(User).filter_by(username=username).first()
    session.close()

    return user


@get_user.register
def _(user_id: int) -> Optional[User]:
    """Get user by id."""

    session = get_session()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()

    return user
