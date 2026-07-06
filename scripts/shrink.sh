#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: shrink.sh <input.mp4> [output.mp4]"
  echo ""
  echo "  input.mp4   Input MP4 file to shrink"
  echo "  output.mp4  Output file name (default: <input>-360p.mp4)"
  echo ""
  echo "Preserves original audio (no re-encode)."
  echo "Video scaled to 360p with H.265 encoding."
  exit 1
fi

INPUT="$1"
OUTPUT="${2:-${INPUT%.*}-360p.mp4}"

if [ "$INPUT" = "$OUTPUT" ]; then
  echo "Error: input and output files must differ"
  exit 1
fi

function human_size {
  numfmt --to=iec-i --suffix=B "$1" 2>/dev/null || echo "$1 bytes"
}

BEFORE=$(stat -f%z "$INPUT" 2>/dev/null || stat -c%s "$INPUT" 2>/dev/null)

ffmpeg -y -i "$INPUT" \
  -vf "scale=-2:360" \
  -c:v libx265 \
  -crf 30 \
  -preset medium \
  -bf 0 \
  -tag:v hvc1 \
  -c:a copy \
  -movflags +faststart \
  "$OUTPUT"

AFTER=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null)

echo ""
echo "Before: $(human_size "$BEFORE")"
echo "After:  $(human_size "$AFTER")"
echo "Saved:  $(human_size $((BEFORE - AFTER))) ($(( 100 * (BEFORE - AFTER) / BEFORE ))%)"
