from fastapi import FastAPI

from app.api.v1.auth import router as auth_router

app = FastAPI(title="作业陪伴助手", version="0.1.0")

app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
