from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.dictation import router as dictation_router
from app.api.v1.submissions import router as submissions_router
from app.api.v1.mistakes import router as mistakes_router
from app.api.v1.tts import router as tts_router
from app.api.v1.admin import router as admin_router

from app.core.config import settings
from app.database import SessionLocal
from app.crud.admin import seed_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: 幂等插入默认管理员
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()
    yield


app = FastAPI(title="作业陪伴助手", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(dictation_router, prefix="/api/v1")
app.include_router(submissions_router, prefix="/api/v1")
app.include_router(mistakes_router, prefix="/api/v1")
app.include_router(tts_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
