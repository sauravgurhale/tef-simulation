"""Analyze a directory of raw MP3 segments and write an analysis report.

Usage:
    python analyze_segments.py --input <raw_segments_dir>
    python analyze_segments.py --input <raw_segments_dir> --output <report_dir>

The script:
  1. Lists all raw_*.mp3 files sorted by name with durations
  2. Flags segments shorter than 2s or longer than 60s
  3. Detects near-duplicate adjacent (and all-pairs) segments via normalized
     cross-correlation of their RMS envelopes (flags pairs with similarity > 0.90)
  4. Writes analysis_report.txt to the output directory (defaults to --input dir)
"""

import argparse
import os
import sys
from glob import glob

from pydub import AudioSegment


# ---------------------------------------------------------------------------
# RMS envelope helpers
# ---------------------------------------------------------------------------

def _rms_envelope(seg: AudioSegment, frame_ms: int = 50) -> list[float]:
    """Return list of RMS values sampled every frame_ms milliseconds."""
    envelope: list[float] = []
    step = frame_ms
    for start in range(0, len(seg), step):
        chunk = seg[start:start + step]
        envelope.append(chunk.rms)
    return envelope


def _norm_cross_correlation(a: list[float], b: list[float]) -> float:
    """Normalized cross-correlation at zero lag (Pearson-style similarity)."""
    if not a or not b:
        return 0.0

    # Trim to same length
    n = min(len(a), len(b))
    a = a[:n]
    b = b[:n]

    mean_a = sum(a) / n
    mean_b = sum(b) / n

    num = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    denom_a = sum((x - mean_a) ** 2 for x in a) ** 0.5
    denom_b = sum((y - mean_b) ** 2 for y in b) ** 0.5

    if denom_a == 0 or denom_b == 0:
        return 1.0 if denom_a == denom_b else 0.0

    return num / (denom_a * denom_b)


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

SHORT_THRESHOLD_MS = 2_000  # < 2 s  → likely silence artifact
LONG_THRESHOLD_MS = 60_000  # > 60 s → possibly merged
DUP_SIMILARITY = 0.90  # cross-correlation threshold for duplicates


def analyze(input_dir: str, output_dir: str) -> str:
    """Run analysis and return path to written report."""
    pattern = os.path.join(input_dir, "raw_*.mp3")
    files = sorted(glob(pattern))

    if not files:
        raise ValueError(f"No raw_*.mp3 files found in: {input_dir}")

    print(f"Found {len(files)} segments in {input_dir}")

    # Load all segments and compute durations
    segments: list[tuple[str, AudioSegment]] = []
    for path in files:
        audio = AudioSegment.from_file(path, format="mp3")
        segments.append((os.path.basename(path), audio))

    # Build report lines
    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("SEGMENT ANALYSIS REPORT")
    lines.append("=" * 70)
    lines.append("")

    # Section 1: Duration table
    lines.append(f"{'#':<6} {'Filename':<20} {'Duration(ms)':>14}  Flags")
    lines.append("-" * 60)
    flags_map: dict[str, list[str]] = {name: [] for name, _ in segments}

    for i, (name, seg) in enumerate(segments, start=1):
        dur = len(seg)
        seg_flags: list[str] = []
        if dur < SHORT_THRESHOLD_MS:
            seg_flags.append(f"SHORT(<{SHORT_THRESHOLD_MS//1000}s)")
        if dur > LONG_THRESHOLD_MS:
            seg_flags.append(f"LONG(>{LONG_THRESHOLD_MS//1000}s)")
        flags_map[name].extend(seg_flags)
        flag_str = ", ".join(seg_flags) if seg_flags else ""
        lines.append(f"{i:<6} {name:<20} {dur:>14}  {flag_str}")

    lines.append("")

    # Section 2: Duplicate detection
    lines.append("=" * 70)
    lines.append("DUPLICATE DETECTION  (similarity > {:.0%})".format(DUP_SIMILARITY))
    lines.append("=" * 70)
    lines.append("")

    print("Computing RMS envelopes…")
    envelopes = [(name, _rms_envelope(seg)) for name, seg in segments]

    dup_pairs: list[tuple[str, str, float]] = []

    # Check all pairs (not just adjacent — duplicates may not be consecutive)
    n = len(envelopes)
    for i in range(n):
        for j in range(i + 1, n):
            name_i, env_i = envelopes[i]
            name_j, env_j = envelopes[j]
            # Skip if duration difference > 30%
            dur_i = len(segments[i][1])
            dur_j = len(segments[j][1])
            if dur_i == 0 or dur_j == 0:
                continue
            ratio = min(dur_i, dur_j) / max(dur_i, dur_j)
            if ratio < 0.70:
                continue
            sim = _norm_cross_correlation(env_i, env_j)
            if sim >= DUP_SIMILARITY:
                dup_pairs.append((name_i, name_j, sim))
                flags_map[name_i].append(f"DUP-with-{name_j}({sim:.2f})")
                flags_map[name_j].append(f"DUP-with-{name_i}({sim:.2f})")

    if dup_pairs:
        lines.append(f"{'File A':<20} {'File B':<20} {'Similarity':>12}")
        lines.append("-" * 55)
        for name_i, name_j, sim in dup_pairs:
            lines.append(f"{name_i:<20} {name_j:<20} {sim:>12.4f}")
    else:
        lines.append("No duplicate pairs detected above threshold.")

    lines.append("")

    # Section 3: Summary of flagged segments
    lines.append("=" * 70)
    lines.append("FLAGGED SEGMENTS SUMMARY")
    lines.append("=" * 70)
    lines.append("")
    any_flagged = False
    for name, seg_flags in flags_map.items():
        if seg_flags:
            lines.append(f"  {name}: {', '.join(seg_flags)}")
            any_flagged = True
    if not any_flagged:
        lines.append("  (none)")

    lines.append("")
    lines.append("=" * 70)
    lines.append("END OF REPORT")
    lines.append("=" * 70)

    report_text = "\n".join(lines) + "\n"

    # Print to stdout
    print("\n" + report_text)

    # Write to file
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "analysis_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"Report written to: {report_path}")
    return report_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze raw MP3 segments and detect duplicates/anomalies."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Directory containing raw_*.mp3 files.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Directory to write analysis_report.txt (default: same as --input).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not os.path.isdir(args.input):
        print(f"Error: input directory not found: {args.input}", file=sys.stderr)
        raise SystemExit(1)

    output_dir = args.output or args.input

    try:
        analyze(args.input, output_dir)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
