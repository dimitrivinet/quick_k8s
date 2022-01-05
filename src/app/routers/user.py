from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends

from app.utils import auth
from app import database

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/resources")
async def get_user_resources(
    current_user: auth.User = Depends(auth.get_current_active_user),
):
    """Get all resources deployed by current user."""

    user_db = database.users.get_user(current_user.username)
    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User unknown in database.",
        )

    resources = database.resources.get_user_resources(user_db.id)

    ret: dict = {"online": [], "deleted": []}
    for resource in resources:
        if resource.deleted_timestamp is not None:
            ret["deleted"].append(resource)
        else:
            ret["online"].append(resource)

    return ret


@router.get("/me", response_model=auth.User)
async def read_own_info(
    current_user: auth.User = Depends(auth.get_current_active_user),
):
    """Get current user info."""

    return current_user
