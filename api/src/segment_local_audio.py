"""Segment a local MP3 file into raw chunks using silence detection.

Usage:
    python segment_local_audio.py --input <path/to/file.mp3> --output <output_dir>
    python segment_local_audio.py --input <path/to/file.mp3> --output <output_dir> \
        --min-silence 3500 --silence-thresh -50 --keep-silence 500

Outputs raw_001.mp3, raw_002.mp3, … to the output directory and prints a
report table showing index, duration (ms), and filename.
"""

import argparse
import os
import sys
import time

from pydub import AudioSegment
from pydub import silence as pydub_silence


def segment_audio(
    input_path: str,
    output_dir: str,
    min_silence_len_ms: int = 3500,
    silence_thresh_db: int | None = None,
    keep_silence_ms: int = 500,
    downsample_rate_hz: int = 16000,
    downsample_channels: int = 1,
) -> list[str]:
    """Segment input MP3 by silence and write numbered raw files.

    Returns list of written file paths.
    """
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading audio: {input_path}")
    audio = AudioSegment.from_file(input_path, format="mp3")
    print(f"  Duration: {len(audio) / 1000:.1f}s")

    print("Downsampling…")
    downsampled = audio.set_frame_rate(downsample_rate_hz).set_channels(downsample_channels)

    thresh = silence_thresh_db if silence_thresh_db is not None else int(downsampled.dBFS - 50)
    print(f"Segmenting (min_silence={min_silence_len_ms}ms, thresh={thresh}dBFS)…")
    t0 = time.time()
    segments = list(
        pydub_silence.split_on_silence(
            downsampled,
            min_silence_len=min_silence_len_ms,
            silence_thresh=thresh,
            keep_silence=keep_silence_ms,
        )
    )
    print(f"  Found {len(segments)} segments in {time.time() - t0:.1f}s")

    output_paths: list[str] = []
    print("\n{:<6} {:>12}  {}".format("Index", "Duration(ms)", "Filename"))
    print("-" * 40)
    for i, seg in enumerate(segments, start=1):
        filename = f"raw_{i:03d}.mp3"
        path = os.path.join(output_dir, filename)
        seg.export(path, format="mp3")
        output_paths.append(path)
        print(f"{i:<6} {len(seg):>12}  {filename}")

    print(f"\nWrote {len(output_paths)} segments to: {output_dir}")
    return output_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Segment a local MP3 into raw chunks using silence detection."
    )
    parser.add_argument("--input", required=True, help="Path to input MP3 file.")
    parser.add_argument("--output", required=True, help="Output directory for raw segments.")
    parser.add_argument(
        "--min-silence",
        type=int,
        default=3500,
        help="Minimum silence length in ms to split on (default: 3500).",
    )
    parser.add_argument(
        "--silence-thresh",
        type=int,
        default=None,
        help="Silence threshold in dBFS (default: audio.dBFS - 50).",
    )
    parser.add_argument(
        "--keep-silence",
        type=int,
        default=500,
        help="Milliseconds of silence to keep at start/end of each chunk (default: 500).",
    )
    parser.add_argument(
        "--downsample-rate",
        type=int,
        default=16000,
        help="Sample rate for downsampling before detection (default: 16000).",
    )
    parser.add_argument(
        "--downsample-channels",
        type=int,
        default=1,
        help="Number of channels after downsampling (default: 1).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        raise SystemExit(1)

    segment_audio(
        input_path=args.input,
        output_dir=args.output,
        min_silence_len_ms=args.min_silence,
        silence_thresh_db=args.silence_thresh,
        keep_silence_ms=args.keep_silence,
        downsample_rate_hz=args.downsample_rate,
        downsample_channels=args.downsample_channels,
    )


if __name__ == "__main__":
    main()
