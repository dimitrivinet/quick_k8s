from fastapi import APIRouter

from app.routers.admin import database


router = APIRouter(prefix="/admin")

router.include_router(database.router)
