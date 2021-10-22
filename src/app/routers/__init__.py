from fastapi import APIRouter

from app.routers import k8s, auth, user, admin

router = APIRouter()

router.include_router(admin.router)
router.include_router(k8s.router)
router.include_router(user.router)
router.include_router(auth.router)
