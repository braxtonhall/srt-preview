import argparse
import sys
import time
from deep_translator import GoogleTranslator


def parse_srt(filepath):
    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    blocks = content.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        index = int(lines[0].strip())
        timing = lines[1].strip()
        text = "\n".join(line.strip() for line in lines[2:])
        entries.append((index, timing, text))
    return entries


def main():
    parser = argparse.ArgumentParser(description="Translate SRT subtitles")
    parser.add_argument("input", help="Input SRT file")
    parser.add_argument("-o", "--output", help="Output SRT file (default: input_en.srt)")
    parser.add_argument("--source", default="zh-CN", help="Source language (default: zh-CN)")
    parser.add_argument("--target", default="en", help="Target language (default: en)")
    parser.add_argument("--delay", type=float, default=0.3,
                        help="Seconds between lines (default: 0.3)")
    args = parser.parse_args()

    output_path = args.output or args.input.rsplit(".", 1)[0] + "_en.srt"
    entries = parse_srt(args.input)
    print(f"Loaded {len(entries)} subtitle segments", flush=True)

    translator = GoogleTranslator(source=args.source, target=args.target)
    translated = []

    for i, (idx, timing, text) in enumerate(entries):
        if i % 25 == 0:
            print(f"  Translating {i + 1}/{len(entries)}...", flush=True)
        for attempt in range(3):
            try:
                result = translator.translate(text)
                translated.append((idx, timing, result.strip()))
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                else:
                    print(f"  FAIL[{idx}]: {text[:40]}...", flush=True)
                    translated.append((idx, timing, text))
        time.sleep(args.delay)

    with open(output_path, "w", encoding="utf-8") as f:
        for idx, timing, text in translated:
            f.write(f"{idx}\n{timing}\n{text}\n\n")

    print(f"Wrote {len(translated)} segments to {output_path}")


if __name__ == "__main__":
    main()
