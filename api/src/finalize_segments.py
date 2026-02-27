"""Finalize raw segments into 44 numbered segment files for a CO practice.

Reads a segment_map.json that specifies which raw files map to each target
segment number (1–44), then copies or combines them into segment_01.mp3 …
segment_44.mp3 in the output directory.

Usage:
    python finalize_segments.py --map /tmp/co_1_raw/segment_map.json \
        --output /path/to/co_web_content/practice_1/audio

segment_map.json format:
{
  "assignments": [
    {"target": 1,  "sources": ["raw_002.mp3"]},
    {"target": 2,  "sources": ["raw_003.mp3"]},
    {"target": 5,  "sources": ["raw_006.mp3", "raw_007.mp3"]},
    ...
  ],
  "drop": ["raw_001.mp3", "raw_004.mp3"]
}

- sources with 1 file  → copy directly
- sources with >1 file → concatenate via combine_audio_files()
- "drop" is informational only (listed for reference, not processed)
- Validates exactly 44 output files are produced
"""

import argparse
import json
import os
import shutil
import sys

from combine_audio_files import combine_audio_files

EXPECTED_SEGMENT_COUNT = 44


def finalize(map_path: str, output_dir: str) -> list[str]:
    """Process the segment map and produce final segment files.

    Returns list of written file paths.
    """
    if not os.path.isfile(map_path):
        raise FileNotFoundError(f"Map file not found: {map_path}")

    with open(map_path, encoding="utf-8") as f:
        data = json.load(f)

    assignments: list[dict] = data.get("assignments", [])
    if not assignments:
        raise ValueError("segment_map.json has no 'assignments'")

    raw_dir = os.path.dirname(os.path.abspath(map_path))
    os.makedirs(output_dir, exist_ok=True)

    # Validate all targets are 1–44 and no duplicates
    targets = [a["target"] for a in assignments]
    if sorted(targets) != list(range(1, EXPECTED_SEGMENT_COUNT + 1)):
        missing = set(range(1, EXPECTED_SEGMENT_COUNT + 1)) - set(targets)
        extra = set(targets) - set(range(1, EXPECTED_SEGMENT_COUNT + 1))
        msg_parts = []
        if missing:
            msg_parts.append(f"missing targets: {sorted(missing)}")
        if extra:
            msg_parts.append(f"extra targets: {sorted(extra)}")
        raise ValueError(
            f"assignments must cover targets 1–{EXPECTED_SEGMENT_COUNT} exactly. "
            + "; ".join(msg_parts)
        )

    output_paths: list[str] = []

    for assignment in sorted(assignments, key=lambda a: a["target"]):
        target: int = assignment["target"]
        sources: list[str] = assignment["sources"]

        if not sources:
            raise ValueError(f"Target {target} has empty sources list")

        # Resolve source paths relative to the map file's directory
        abs_sources = [
            src if os.path.isabs(src) else os.path.join(raw_dir, src)
            for src in sources
        ]

        for src_path in abs_sources:
            if not os.path.isfile(src_path):
                raise FileNotFoundError(
                    f"Source file not found for target {target}: {src_path}"
                )

        out_filename = f"segment_{target:02d}.mp3"
        out_path = os.path.join(output_dir, out_filename)

        if len(abs_sources) == 1:
            shutil.copy2(abs_sources[0], out_path)
            print(f"  segment_{target:02d}.mp3  ← {sources[0]}")
        else:
            combine_audio_files(abs_sources, out_path)
            print(f"  segment_{target:02d}.mp3  ← {' + '.join(sources)}")

        output_paths.append(out_path)

    # Final count validation
    if len(output_paths) != EXPECTED_SEGMENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SEGMENT_COUNT} output files, "
            f"got {len(output_paths)}"
        )

    return output_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            f"Produce {EXPECTED_SEGMENT_COUNT} final segment_NN.mp3 files "
            "from a segment_map.json."
        )
    )
    parser.add_argument(
        "--map",
        required=True,
        metavar="SEGMENT_MAP_JSON",
        help="Path to segment_map.json.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory for segment_01.mp3 … segment_44.mp3.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print(f"Map:    {args.map}")
    print(f"Output: {args.output}")
    print()

    try:
        paths = finalize(args.map, args.output)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"\nSuccess: wrote {len(paths)} segments to {args.output}")
    print(f"  First: {os.path.basename(paths[0])}")
    print(f"  Last:  {os.path.basename(paths[-1])}")


if __name__ == "__main__":
    main()
