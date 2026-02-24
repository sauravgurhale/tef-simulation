import logging
import os
from io import BytesIO
from typing import cast

# from typing import cast
import time
from dataclasses import dataclass
from pydub import AudioSegment, silence

from supabase_client import SupabaseClient


@dataclass(init=False)
class COAudioSegments:
    """
    Generate audio segments from a given audio file.
    All non-silent audio segments
    """

    def __init__(
        self,
        *,
        supabase_client: SupabaseClient,
        input_format: str = "mp3",
        output_format: str = "mp3",
        # TODO: Will have to play with the silence settings for CO audio
        # 10 sec of silence, works almost well
        # Try 8 seconds and you will have proper segments
        min_silence_len_ms: int = 3500,
        silence_thresh_db: int | None = None,
        keep_silence_ms: int = 500,
        downsample_rate_hz: int = 16000,
        downsample_channels: int = 1,
    ):
        self.supabase_client = supabase_client
        self.input_format = input_format
        self.output_format = output_format
        self.min_silence_len_ms = min_silence_len_ms
        self.silence_thresh_db = silence_thresh_db
        self.keep_silence_ms = keep_silence_ms
        self.downsample_rate_hz = downsample_rate_hz
        self.downsample_channels = downsample_channels
        self.logger = logging.getLogger(__name__)

    def _get_audio_file(self, practice_id: str) -> bytes:
        """
        Get the audio file for a given practice_id.
        """
        return self.supabase_client.get_co_audio(practice_id)

    def _load_audio(self, audio_bytes: bytes) -> AudioSegment:
        audio_buffer = BytesIO(audio_bytes)
        return AudioSegment.from_file(audio_buffer, format=self.input_format)

    def _downsample_audio(self, audio: AudioSegment) -> AudioSegment:
        print("Downsampling")
        return audio.set_frame_rate(self.downsample_rate_hz).set_channels(
            self.downsample_channels
        )

    def _segment_audio(self, audio: AudioSegment) -> list[AudioSegment]:
        print("Segmenting audio")
        silence_thresh = (
            self.silence_thresh_db
            if self.silence_thresh_db is not None
            else int(audio.dBFS - 50)
        )
        print("Silence threshold", silence_thresh)
        # start timer
        start_time = time.time()
        segments = list(
            silence.split_on_silence(
                audio,
                min_silence_len=self.min_silence_len_ms,
                silence_thresh=silence_thresh,
                keep_silence=self.keep_silence_ms,
            )
        )
        end_time = time.time()
        print("Time taken for segmenting at silence", end_time - start_time)
        return cast(list[AudioSegment], segments)

    def generate_audio_segments(self, practice_id: str) -> list[bytes]:
        audio_bytes = self._get_audio_file(practice_id)
        audio = self._load_audio(audio_bytes)
        print("Loaded audio")
        downsampled = self._downsample_audio(audio)
        print("Downsampled audio")
        segments = self._segment_audio(downsampled)
        print("Segmented audio")

        print("Now generating output audio segments")
        # start timer
        start_time = time.time()
        output_segments: list[bytes] = []
        for segment in segments:
            buffer = BytesIO()
            segment.export(buffer, format=self.output_format)
            output_segments.append(buffer.getvalue())
        end_time = time.time()
        print("Time taken for generating output audio segments", end_time - start_time)
        return output_segments

    def write_audio_segments(
        self,
        practice_id: str,
        output_dir: str,
    ) -> list[str]:
        os.makedirs(output_dir, exist_ok=True)
        self.logger.info("Generating audio segments for practice %s", practice_id)
        segments = self.generate_audio_segments(practice_id)

        print("Now writing audio segments to disk")
        # start timer
        start_time = time.time()
        output_paths: list[str] = []
        extension = self.output_format.lower()
        for index, segment_bytes in enumerate(segments, start=1):
            filename = f"segment_{index:02d}.{extension}"
            path = os.path.join(output_dir, filename)
            self.logger.debug("Writing segment %d to %s", index, path)
            with open(path, "wb") as segment_file:
                segment_file.write(segment_bytes)
            output_paths.append(path)

        end_time = time.time()
        print("Time taken for writing audio segments to disk", end_time - start_time)

        return output_paths


if __name__ == "__main__":
    try:
        practice_id = "71d05eef-8b8f-4aaf-baa2-00bc38c8ce86"
        path = (
            "/Users/saurav.gurhale/Desktop/github/tef-simulation/"
            "api/src/all_co_audio_segments/co_19_test_three_com"
        )
        supabase_client = SupabaseClient()
        segmenter = COAudioSegments(
            supabase_client=supabase_client,
        )
        paths = segmenter.write_audio_segments(
            practice_id,
            path,
        )
        print("\n".join(paths))
    except Exception as exc:
        print(f"Error: {exc}")
        raise exc
