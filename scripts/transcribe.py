import argparse
import os
import sys
from faster_whisper import WhisperModel


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def transcribe(video_path: str, output_path: str, model_size: str = "large-v3",
               device: str = "auto", compute_type: str = "auto"):
    if not os.path.exists(video_path):
        print(f"Error: video not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading model {model_size} (this may download ~3GB on first run)...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    print(f"Transcribing: {video_path}")
    segments, info = model.transcribe(
        video_path,
        language="zh",
        beam_size=5,
        vad_filter=True,
        word_timestamps=False,
    )

    print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
    print(f"Duration: {info.duration:.1f}s")

    entries = []
    for segment in segments:
        start = format_timestamp(segment.start)
        end = format_timestamp(segment.end)
        text = segment.text.strip()
        print(f"  [{start} -> {end}] {text}")
        entries.append((start, end, text))

    with open(output_path, "w", encoding="utf-8") as f:
        for i, (start, end, text) in enumerate(entries, 1):
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    print(f"\nWrote {len(entries)} segments to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Transcribe video to SRT using faster-whisper")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("-o", "--output", help="Output SRT path (default: <video basename>.srt)")
    parser.add_argument("-m", "--model", default="large-v3",
                        help="Model size (default: large-v3)")
    parser.add_argument("-d", "--device", default="auto",
                        help="Device: auto, cpu, cuda (default: auto)")
    parser.add_argument("-c", "--compute-type", default="auto",
                        help="Compute type: auto, int8, float16, etc. (default: auto)")
    args = parser.parse_args()

    if args.output:
        output_path = args.output
    else:
        base = os.path.splitext(os.path.basename(args.video))[0]
        output_path = f"{base}.srt"

    transcribe(args.video, output_path, args.model, args.device, args.compute_type)


if __name__ == "__main__":
    main()
