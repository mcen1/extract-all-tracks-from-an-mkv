#!/usr/bin/env bash

set -euo pipefail

INPUT="$1"

if [[ -z "${INPUT:-}" ]]; then
  echo "Usage: $0 <input.mkv>"
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "File not found: $INPUT"
  exit 1
fi

BASENAME="$(basename "$INPUT" .mkv)"

echo "Probing audio streams..."

# Get audio stream indices + codec names
mapfile -t STREAMS < <(ffprobe -v error \
  -select_streams a \
  -show_entries stream=index,codec_name \
  -of csv=p=0 "$INPUT")

if [[ ${#STREAMS[@]} -eq 0 ]]; then
  echo "No audio streams found."
  exit 0
fi

echo "Found ${#STREAMS[@]} audio stream(s). Extracting..."

for entry in "${STREAMS[@]}"; do
  INDEX=$(echo "$entry" | cut -d',' -f1)
  CODEC=$(echo "$entry" | cut -d',' -f2)

  # Choose extension based on codec
  case "$CODEC" in
    aac) EXT="m4a" ;;
    ac3) EXT="ac3" ;;
    eac3) EXT="eac3" ;;
    dts) EXT="dts" ;;
    mp3) EXT="mp3" ;;
    flac) EXT="flac" ;;
    opus) EXT="opus" ;;
    vorbis) EXT="ogg" ;;
    *) EXT="bin" ;;
  esac

  OUTPUT="${BASENAME}_audio_${INDEX}.${EXT}"

  echo "Extracting stream $INDEX ($CODEC) -> $OUTPUT"

  ffmpeg -y -i "$INPUT" \
    -map 0:"$INDEX" \
    -c copy \
    "$OUTPUT"
done

echo "Done."
