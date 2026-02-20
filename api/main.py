import os

import uvicorn
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Supabase Audio Proxy")


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise HTTPException(status_code=500, detail=f"Missing env var: {name}")
    return value


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/audio/{object_path:path}")
async def fetch_audio(object_path: str):
    pass


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
