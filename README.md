# KVU Downloader

Audiobook downloader for knigavuhe.org with multithreaded downloads and Rich progress display.

## Features

- Multithreaded downloads (configurable)
- Book cover auto-download
- Automatic retries on failure
- Full URL or slug input

## Requirements

- Python 3.8+

## Installation

```bash
git clone https://github.com/idoo/KVU_downloader && cd KVU_downloader && uv sync
```

## Usage

```bash
kvu-download zapiski-okhotnika              # by slug
kvu-download anafem -t 8 -o ~/audiobooks/   # 8 threads, custom dir
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `-t, --threads N` | Download threads | `4` |
| `-o, --output DIR` | Output directory | Book slug |
| `-f, --format FMT` | Filename format | `"{title} {name}"` |
| `--cover-only` | Only download cover | |
| `--no-cover` | Skip cover download | |
| `-V, --version` | Show version | |

### Format Variables

- `{title}` - Track title
- `{num}` - Track number (0-indexed)
- `{name}` - Book slug

## Example Output

```
Fetching book data from https://knigavuhe.org/book/zapiski-okhotnika/
Book: Записки охотника
  Author: Иван Тургенев
  Downloading cover image...
 + Downloaded cover.jpg (156.2KB)
  Resolved 25 tracks
Downloading 25 files using 4 threads
⠸ Downloading 25 tracks... ━━━━━━━━━━━━━━━━ 312.5MB 3.2MB/s 0:01:23

 + Downloaded 25 files (892.5MB) in 4m 38s
 + Completed in 4m 39s
```

## License

MIT
