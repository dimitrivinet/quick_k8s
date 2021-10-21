from fastapi import APIRouter

from app.routers import k8s, auth

router = APIRouter()

router.include_router(k8s.router)
router.include_router(auth.router)
