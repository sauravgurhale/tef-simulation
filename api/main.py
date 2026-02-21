import mimetypes

import uvicorn
from fastapi import FastAPI, HTTPException, Response

from api.src.supabase_client import SupabaseClient

app = FastAPI(title="Supabase Audio Proxy")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/audio/{practice_id}")
async def fetch_full_co_audio(practice_id: str) -> Response:
    """Fetch the full audio for a given practice_id"""
    try:
        supabase_client = SupabaseClient()
        content = supabase_client.get_co_audio(practice_id)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Audio not found") from exc

    return Response(
        content=content,
        media_type=mimetypes.types_map.get(".mp3", "application/octet-stream"),
    )


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
