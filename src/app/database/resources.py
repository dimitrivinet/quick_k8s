"""API for accessing the resources table in the database."""

from datetime import datetime
from functools import singledispatch
from typing import List, Optional

from app.database.orm import Resource
from app.database.utils import get_session


def add_resource(resource: Resource) -> None:
    """Add resource to database."""

    session = get_session()
    session.add(resource)
    session.commit()


def delete_resource(resource: Resource) -> None:
    """Delete resource from database."""

    session = get_session()
    session.delete(resource)
    session.commit()


def fake_delete_resource(resource: Resource) -> None:
    """Delete resource from database."""

    session = get_session()
    resource = session.query(Resource).filter_by(id=resource.id).first()
    resource.deleted_timestamp = datetime.now()
    session.commit()
    session.close()


@singledispatch
def get_resource(resource_name: str, owner_id: int) -> Optional[Resource]:
    """Get resource by username."""

    session = get_session()
    resource = (
        session.query(Resource)
        .filter_by(
            owner=owner_id,
            name=resource_name,
        )
        .first()
    )
    session.close()

    return resource


@get_resource.register
def _(resource_id: int, owner_id: int) -> Optional[Resource]:  # type: ignore
    """Get resource by id."""

    session = get_session()
    resource = (
        session.query(Resource)
        .filter_by(
            owner=owner_id,
            id=resource_id,
        )
        .first()
    )
    session.close()

    return resource


def get_all_resources() -> List[Resource]:
    """Get all resources in the database."""

    session = get_session()
    resource = session.query(Resource).all()
    session.close()

    return resource


def get_user_resources(owner_id: int) -> List[Resource]:
    """Get all resources for a user by owner id."""

    session = get_session()
    resource = session.query(Resource).filter_by(owner=owner_id).all()
    session.close()

    return resource


def set_update_time(resource_name: str, owner_id: int, new_timestamp):
    session = get_session()
    resource = (
        session.query(Resource)
        .filter_by(
            owner=owner_id,
            name=resource_name,
        )
        .first()
    )

    resource.modified_timestamp = new_timestamp
    session.commit()

    session.close()
