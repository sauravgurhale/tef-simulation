import os

from supabase import create_client
from pydantic import BaseModel


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing env var: {name}")
    return value


class Supabase(BaseModel):
    def __init__(self):
        url = get_env("SUPABASE_URL")
        key = get_env("SUPABASE_SERVICE_ROLE_KEY")

        self._client = create_client(url, key)

    def get_co_audio(self, practice_id: str) -> None:
        """For a given practice_id, get the full audio for that practice"""
        # returns the audio file?
        pass

    def get_co_practice_id(title: str) -> str:
        """Get the practice_id for a given co title"""
        pass

    def post_co_audio_segments(self) -> None:
        pass
