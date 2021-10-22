from fastapi import APIRouter

from app.routers import k8s, auth, user, database

router = APIRouter()

router.include_router(k8s.router)
router.include_router(auth.router)
router.include_router(user.router)
router.include_router(database.router)
