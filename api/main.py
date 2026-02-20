import os
from urllib.parse import quote

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

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