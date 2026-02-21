import os

from supabase import create_client
from pydantic import BaseModel


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing env var: {name}")
    return value


class SupabaseClient(BaseModel):
    def __init__(self):
        _url = get_env("SUPABASE_URL")
        _key = get_env("SUPABASE_SERVICE_ROLE_KEY")

        # tables
        self._co_table = "practices_co"
        self._practice_audio_table = "practice_co_full_audio"
        self._audio_segments_table = "audio_segments"

        # client
        self._client = create_client(_url, _key)

    def get_co_audio(self, practice_id: str) -> bytes:
        """For a given practice_id, get the full audio for that practice"""
        # get file path
        file_path = (
            self._client.table(self._practice_audio_table)
            .select("storage_path")
            .eq("practice_id", practice_id)
            .execute()
            .data[0]["storage_path"]
        )
        bucket, audio_path = file_path.split("/")
        content = self._client.storage.from_(bucket).download(audio_path)

        return content

    def get_storage_object(self, bucket: str, object_path: str) -> bytes:
        """Download a storage object and return raw bytes."""
        return self._client.storage.from_(bucket).download(object_path)

    def get_co_practice_id(self, title: str) -> str:
        """Get the practice_id for a given co title"""
        return (
            self._client.table("practices_co")
            .select("id")
            .eq("title", title)
            .execute()
            .data[0]["id"]
        )

    def post_co_audio_segments(self) -> None:
        pass
