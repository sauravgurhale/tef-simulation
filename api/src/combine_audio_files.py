import argparse
import os
import sys

from pydub import AudioSegment


def combine_audio_files(input_paths: list[str], output_path: str) -> str:
    """Combine MP3 files in input order and write a single MP3 output file."""
    _validate_paths(input_paths, output_path)

    combined = AudioSegment.from_file(input_paths[0], format="mp3")
    for input_path in input_paths[1:]:
        combined += AudioSegment.from_file(input_path, format="mp3")

    combined.export(output_path, format="mp3")
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Combine multiple MP3 files")
    parser.add_argument(
        "--input",
        dest="inputs",
        action="append",
        required=True,
        help="Input MP3 path. Repeat this flag for each file in order.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output MP3 file path.",
    )
    return parser


def _validate_paths(input_paths: list[str], output_path: str) -> None:
    if len(input_paths) < 2:
        raise ValueError("At least two --input files are required")

    for input_path in input_paths:
        if not input_path.lower().endswith(".mp3"):
            raise ValueError(f"Input file must be .mp3: {input_path}")
        if not os.path.isfile(input_path):
            raise ValueError(f"Input file does not exist: {input_path}")

    if not output_path.lower().endswith(".mp3"):
        raise ValueError("Output file must end with .mp3")

    output_dir = os.path.dirname(output_path) or "."
    if not os.path.isdir(output_dir):
        raise ValueError(f"Output directory does not exist: {output_dir}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        output_path = combine_audio_files(args.inputs, args.output)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(output_path)


if __name__ == "__main__":
    main()
