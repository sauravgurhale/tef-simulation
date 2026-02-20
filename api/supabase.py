import os
from functools import lru_cache

from supabase import Client, create_client
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
    
    def get_client(self) -> Client:
        return self._client

    def get_co_audio(self, practice_id: str) -> None:
        pass
