import sqlalchemy.exc

from app.database import orm
from app.database.utils import get_session
from app.utils import auth


def populate_roles_table():
    """Fill roles table with correct values."""

    all_roles = [orm.Role(id=role.value, name=role.name) for role in auth.Role]

    session = get_session()
    session.add_all(all_roles)

    try:
        session.commit()
        return True
    except sqlalchemy.exc.IntegrityError:
        return False
