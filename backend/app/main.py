from fastapi import FastAPI

app = FastAPI(title="作业陪伴助手", version="0.1.0")


@app.get("/health")
def health_check():
    return {"status": "ok"}
