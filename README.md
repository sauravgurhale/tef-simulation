# Salut

## Combine audio files

Use the CLI to combine MP3 files in the exact order you pass via repeated `--input` flags.

```bash
python3 -m api.src.combine_audio_files \
  --input /path/to/part1.mp3 \
  --input /path/to/part2.mp3 \
  --output /path/to/combined.mp3
```

Notes:
- Only `.mp3` input/output is supported.
- The output directory must already exist.
- `pydub` requires `ffmpeg` to be installed and available on `PATH`.
