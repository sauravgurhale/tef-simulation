import os
from io import BytesIO

# from typing import cast

from dataclasses import dataclass
from pydub import AudioSegment, silence

from supabase_client import SupabaseClient


@dataclass(init=False)
class COAudioSegments:
    """
    Generate audio segments from a given audio file.
    All non-silent audio segments
    """

    supabase_client: SupabaseClient
    input_format: str = "mp3"
    output_format: str = "wav"
    min_silence_len_ms: int = 1000
    silence_thresh_db: int | None = None
    keep_silence_ms: int = 250

    def __init__(
        self,
        *,
        supabase_client: SupabaseClient,
        input_format: str = "mp3",
        output_format: str = "wav",
        min_silence_len_ms: int = 1000,
        silence_thresh_db: int | None = None,
        keep_silence_ms: int = 250,
    ):
        self.supabase_client = supabase_client
        self.input_format = input_format
        self.output_format = output_format
        self.min_silence_len_ms = min_silence_len_ms
        self.silence_thresh_db = silence_thresh_db
        self.keep_silence_ms = keep_silence_ms

    def _get_audio_file(self, practice_id: str) -> bytes:
        """
        Get the audio file for a given practice_id.
        """
        return self.supabase_client.get_co_audio(practice_id)

    def _load_audio(self, audio_bytes: bytes) -> AudioSegment:
        audio_buffer = BytesIO(audio_bytes)
        return AudioSegment.from_file(audio_buffer, format=self.input_format)

    def _segment_audio(self, audio: AudioSegment) -> list[AudioSegment]:
        silence_thresh = (
            self.silence_thresh_db
            if self.silence_thresh_db is not None
            else int(audio.dBFS - 16)
        )
        return silence.split_on_silence(
            audio,
            min_silence_len=self.min_silence_len_ms,
            silence_thresh=silence_thresh,
            keep_silence=self.keep_silence_ms,
        )

    def generate_audio_segments(self, practice_id: str) -> list[bytes]:
        audio_bytes = self._get_audio_file(practice_id)
        audio = self._load_audio(audio_bytes)
        segments = self._segment_audio(audio)

        output_segments: list[bytes] = []
        for segment in segments:
            buffer = BytesIO()
            segment.export(buffer, format=self.output_format)
            output_segments.append(buffer.getvalue())

        return output_segments

    def write_audio_segments(
        self,
        practice_id: str,
        output_dir: str,
    ) -> list[str]:
        os.makedirs(output_dir, exist_ok=True)
        segments = self.generate_audio_segments(practice_id)

        output_paths: list[str] = []
        extension = self.output_format.lower()
        for index, segment_bytes in enumerate(segments, start=1):
            filename = f"segment_{index:02d}.{extension}"
            path = os.path.join(output_dir, filename)
            with open(path, "wb") as segment_file:
                segment_file.write(segment_bytes)
            output_paths.append(path)

        return output_paths
