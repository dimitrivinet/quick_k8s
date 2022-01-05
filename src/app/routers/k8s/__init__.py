from fastapi import APIRouter

from app.routers.k8s import resources


router = APIRouter(prefix="/k8s")

router.include_router(resources.router)
