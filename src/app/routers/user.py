from fastapi import APIRouter
from fastapi.param_functions import Depends

from app.utils import auth
from app import dummy_db

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/deployments")
async def get_user_deployments(
    current_user: auth.User = Depends(auth.get_current_active_user),
):
    """Get all deployments deployed by current user."""

    return {"deployments": dummy_db.user_deployments.get(current_user.username, [])}


@router.get("/me", response_model=auth.User)
async def read_own_info(
    current_user: auth.User = Depends(auth.get_current_active_user),
):
    """Get current user info."""

    return current_user
