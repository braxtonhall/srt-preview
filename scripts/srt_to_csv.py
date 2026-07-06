import argparse
import csv
import re
import sys


TIMING_RE = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})")


def parse_srt(filepath):
    entries = {}
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue
        index = int(lines[0].strip())
        timing = lines[1].strip()
        text_lines = [line.strip() for line in lines[2:] if line.strip()]
        line1 = text_lines[0] if len(text_lines) > 0 else ""
        line2 = text_lines[1] if len(text_lines) > 1 else ""
        entries[index] = (timing, line1, line2)
    return entries


def main():
    parser = argparse.ArgumentParser(description="Merge source and translation SRTs into Google Sheets CSV")
    parser.add_argument("source", help="Source language SRT (e.g. Cantonese)")
    parser.add_argument("translation", help="Translation SRT (e.g. English)")
    parser.add_argument("-o", "--output", default="subtitles.csv", help="Output CSV path")
    args = parser.parse_args()

    source = parse_srt(args.source)
    translation = parse_srt(args.translation)

    all_indices = sorted(set(source.keys()) | set(translation.keys()))

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["\u2705", "\u26a0\ufe0f", "Start", "End",
                         "Source 1", "Source 2", "Translation 1", "Translation 2"])
        for idx in all_indices:
            timing = source.get(idx, translation.get(idx, ("00:00:00,000 --> 00:00:01,000", "", "")))[0]
            m = TIMING_RE.match(timing)
            if m:
                start, end = m.group(1), m.group(2)
            else:
                start, end = timing, ""

            src_data = source.get(idx, ("", "", ""))
            trans_data = translation.get(idx, ("", "", ""))

            writer.writerow([
                "FALSE", "FALSE",
                start, end,
                src_data[1], src_data[2],
                trans_data[1], trans_data[2],
            ])

    print(f"Written {len(all_indices)} rows to {args.output}")


if __name__ == "__main__":
    main()
