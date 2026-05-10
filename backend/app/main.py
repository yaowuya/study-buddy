from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.dictation import router as dictation_router
from app.api.v1.submissions import router as submissions_router
from app.api.v1.mistakes import router as mistakes_router

app = FastAPI(title="作业陪伴助手", version="0.1.0")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(dictation_router, prefix="/api/v1")
app.include_router(submissions_router, prefix="/api/v1")
app.include_router(mistakes_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
