from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends
import sqlalchemy.exc

from app import database
from app.utils import auth

router = APIRouter(prefix="/db", tags=["database"])


@router.get("/users")
def get_users(
    _: auth.UserInDB = Depends(auth.current_user_is_admin)
):
    """Get all users in database."""

    session = database.get_session()
    users = session.query(database.User)

    all_users = list(users)

    return {"all_users": all_users}


@router.post("/users")
def add_user(
    user: auth.User,
    password: auth.Password,
    # _: auth.UserInDB = Depends(auth.current_user_is_admin)
):
    """Add new user."""

    if not password.is_hashed:
        hashed_password = auth.get_password_hash(password.password)
    else:
        hashed_password=password.password

    role = auth.Role[user.role]

    new_user = database.User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        disabled=user.disabled,
        role=role.value,
    )

    try:
        database.users.add_user(new_user)
    except sqlalchemy.exc.IntegrityError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from None

    return {"result": "Success"}


@router.get("/user/{user_id}")
def get_one_user(
    user_id: int,
    _: auth.UserInDB = Depends(auth.current_user_is_admin)
):
    """Get one user by id."""

    user = database.users.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with id {user_id} in database.",
        )

    return {"user": user}



@router.delete("/user/{user_id}")
def delete_user(
    user_id: int,
    _: auth.UserInDB = Depends(auth.current_user_is_admin)
):
    """Delete a user."""

    user = database.users.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with id {user_id} in database.",
        )

    database.users.delete_user(user)

    return {"result": "Success"}
