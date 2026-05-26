# sub-preview

Video preview app with encrypted videos and Google Sheets-backed subtitles.

## Scripts

### `scripts/convert.sh` — MKV to small MP4

Converts a large MKV file to a tiny 144p MP4 for bandwidth-efficient encrypted previews.

```bash
./scripts/convert.sh input.mkv [output.mp4]
```

Settings:
- **Resolution**: scaled to 144p height (width auto-calculated)
- **Codec**: HEVC (libx265) with CRF 32
- **Audio**: AAC 32 kbps
- **Framerate**: unchanged from source

Requires `ffmpeg` with `libx265` support.

### `scripts/encrypt.mjs` — Encrypt MP4

Encrypts an MP4 for use with the player. Prints salt and hash to paste into `index.html`.

```bash
node scripts/encrypt.mjs input.mp4 output.enc password
```
