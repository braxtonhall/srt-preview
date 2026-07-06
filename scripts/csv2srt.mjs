import { writeFileSync } from 'fs';

const DEFAULT_URL =
  'https://docs.google.com/spreadsheets/d/145FBocTawJJCysa0fj9YrNAVc5Ob-4GTrrJRrXcR-_o/export?format=csv&gid=142222312';
const csvUrl = process.argv[2] || DEFAULT_URL;
const outputPath = process.argv[3] || 'subtitles.srt';

function parseCSV(text) {
  const rows = [];
  const lines = text.split('\n');

  for (const line of lines) {
    if (!line.trim()) continue;
    const fields = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (inQuotes) {
        if (ch === '"') {
          if (i + 1 < line.length && line[i + 1] === '"') {
            current += '"';
            i++;
          } else {
            inQuotes = false;
          }
        } else {
          current += ch;
        }
      } else {
        if (ch === '"') {
          inQuotes = true;
        } else if (ch === ',') {
          fields.push(current);
          current = '';
        } else {
          current += ch;
        }
      }
    }
    fields.push(current);
    rows.push(fields);
  }

  return rows;
}

function parseTimestamp(ts) {
  const parts = ts.split(':');
  const hours = parseInt(parts[0], 10);
  const minutes = parseInt(parts[1], 10);
  const secMs = parts[2].split(',');
  const seconds = parseInt(secMs[0], 10);
  const ms = parseInt(secMs[1], 10);
  return hours * 3600 + minutes * 60 + seconds + ms / 1000;
}

function toSrtTime(totalSeconds) {
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = Math.floor(totalSeconds % 60);
  const ms = Math.round((totalSeconds - Math.floor(totalSeconds)) * 1000);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')},${String(ms).padStart(3, '0')}`;
}

async function main() {
  console.error(`Fetching: ${csvUrl}`);
  const resp = await fetch(csvUrl);
  if (!resp.ok) {
    console.error(`HTTP ${resp.status}: ${resp.statusText}`);
    process.exit(1);
  }
  const text = await resp.text();
  const rows = parseCSV(text);

  if (rows.length < 2) {
    console.error('No subtitle rows found');
    process.exit(1);
  }

  const entries = [];
  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (row.length < 8) continue;

    const trans1 = (row[6] || '').trim();
    const trans2 = (row[7] || '').trim();
    const text = [trans1, trans2].filter(Boolean).join('\n');
    if (!text) continue;

    entries.push({
      start: parseTimestamp(row[2]),
      end: parseTimestamp(row[3]),
      text,
    });
  }

  const srt = entries
    .map((entry, i) => {
      return `${i + 1}\n${toSrtTime(entry.start)} --> ${toSrtTime(entry.end)}\n${entry.text}\n`;
    })
    .join('\n');

  writeFileSync(outputPath, srt, 'utf-8');
  console.error(`Wrote ${entries.length} subtitles to ${outputPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
