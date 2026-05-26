#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: convert.sh <input.mkv> [output.mp4]"
  echo ""
  echo "  input.mkv   Input MKV file to convert"
  echo "  output.mp4  Output file name (default: same as input with .mp4 extension)"
  exit 1
fi

INPUT="$1"
OUTPUT="${2:-${INPUT%.*}.mp4}"

ffmpeg -i "$INPUT" \
  -vf "scale=-2:144" \
  -c:v libx265 \
  -crf 32 \
  -preset veryslow \
  -c:a aac \
  -b:a 32k \
  -movflags +faststart \
  "$OUTPUT"
