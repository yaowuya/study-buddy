from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .families import router as families_router
from .tasks import router as tasks_router

router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(auth_router, prefix="/auth")
router.include_router(users_router, prefix="/users")
router.include_router(families_router, prefix="/families")
router.include_router(tasks_router, prefix="/tasks")
