#!/bin/bash
set -euo pipefail

HAR_FILE="${1:-}"
OUTPUT="${2:-}"

if [ -z "$HAR_FILE" ]; then
    echo "Usage: $0 <har_file> [output_name]"
    echo ""
    echo "  Extracts m3u8 URL from a Firefox HAR file and downloads the video."
    echo "  If output_name is not given, derives it from the HAR filename."
    exit 1
fi

if [ ! -f "$HAR_FILE" ]; then
    echo "Error: File not found: $HAR_FILE"
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "Error: 'jq' is required. Install with: brew install jq"
    exit 1
fi

if ! command -v yt-dlp &>/dev/null; then
    echo "Error: 'yt-dlp' is required"
    exit 1
fi

M3U8_URLS=$(jq -r '.log.entries[].request.url' "$HAR_FILE" | grep -i '\.m3u8' || true)

if [ -z "$M3U8_URLS" ]; then
    echo "Error: No .m3u8 URL found in HAR file"
    exit 1
fi

# Prefer higher-quality streams: prioritize URLs with "720", "1080", "hd", "high"
# over "360", "480", "sd", "low". Also prefer direct CDN URLs over redirect-proxy URLs.
SCORE_URL() {
    local url="$1"
    local score=0
    [[ "$url" =~ 1080 ]] && score=$((score + 300))
    [[ "$url" =~ 720 ]]  && score=$((score + 200))
    [[ "$url" =~ 480 ]]  && score=$((score + 100))
    [[ "$url" =~ 360 ]]  && score=$((score + 50))
    [[ "$url" =~ [Hh][Dd] ]] && score=$((score + 250))
    [[ "$url" =~ [Hh]igh ]] && score=$((score + 150))
    [[ "$url" =~ [Mm]edium ]] && score=$((score + 80))
    [[ "$url" =~ [Ll]ow|[Ss][Dd] ]] && score=$((score + 30))
    # Prefer direct CDN URLs (not through redirect proxies)
    [[ "$url" =~ ^https?://[^/?]*osqnecdn\. ]] && score=$((score + 1000))
    [[ "$url" =~ ^https?://[^/?]*mddcloud ]] && score=$((score + 1000))
    [[ "$url" =~ ^https?://[^/?]*myqcloud ]] && score=$((score + 1000))
    echo "$score"
}

BEST_URL=""
BEST_SCORE=-1

while IFS= read -r url; do
    s=$(SCORE_URL "$url")
    if [ "$s" -gt "$BEST_SCORE" ]; then
        BEST_SCORE="$s"
        BEST_URL="$url"
    fi
done <<< "$M3U8_URLS"

echo "Found $(echo "$M3U8_URLS" | wc -l | tr -d ' ') m3u8 URL(s)"
echo "Selected: $BEST_URL"
echo ""

if [ -z "$OUTPUT" ]; then
    OUTPUT="$(basename "$HAR_FILE" .har | sed 's/_Archive.*//').mp4"
fi

yt-dlp --referer "https://www.mddcloud.com.cn/" -o "$OUTPUT" "$BEST_URL"

echo ""
echo "Done: $OUTPUT"
ls -lh "$OUTPUT"
