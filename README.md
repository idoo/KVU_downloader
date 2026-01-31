# KVU Downloader

Audiobook downloader for knigavuhe.org with UV-style progress display and multithreaded downloads.

## Features

- **UV-style progress display** - Beautiful terminal output using Rich library
- **Multithreaded downloads** - Configurable concurrent downloads
- **Book cover download** - Automatically downloads cover image before audio
- **Book info extraction** - Displays book title and author
- **Full URL support** - Paste complete URLs or just the book ending
- **Flexible output** - Custom output directory and filename formats
- **Automatic retries** - Failed downloads retry up to 3 times
- **Fallback support** - Works with tqdm if Rich is not available

## Installation

### Using uv (Recommended)

```bash
git clone https://github.com/petrarka/KVU_downloader
cd KVU_downloader
uv sync
```

### Using pip

```bash
git clone https://github.com/petrarka/KVU_downloader
cd KVU_downloader
pip install -e .
```

## Usage

```bash
kvu-download [OPTIONS] URL
```

Or using uv directly:

```bash
uv run kvu-download [OPTIONS] URL
```

### Examples

```bash
# Download using full URL
kvu-download https://knigavuhe.org/book/zapiski-okhotnika/

# Download using just the ending
kvu-download zapiski-okhotnika

# Use 8 download threads
kvu-download anafem -t 8

# Custom filename format
kvu-download anafem -f "#{num} - {title}"

# Custom output directory
kvu-download anafem -o ~/audiobooks/turgenev/

# Download only the cover image
kvu-download anafem --cover-only

# Skip cover download
kvu-download anafem --no-cover
```

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `URL` | Book URL or ending | Required |
| `-t, --threads N` | Number of download threads | `4` |
| `-f, --format FMT` | Filename format string | `"{title} {name}"` |
| `-o, --output DIR` | Output directory | Book ending |
| `--no-cover` | Skip cover image download | `false` |
| `--cover-only` | Only download cover image | `false` |
| `-V, --version` | Show version and exit | |
| `-h, --help` | Show help message | |

## Filename Format Variables

| Variable | Description |
|----------|-------------|
| `{title}` | Track title from the audiobook |
| `{num}` | Track number (0-indexed) |
| `{name}` | Book ending/slug |

### Format Examples

```bash
# Default: "Chapter 1 anafem.mp3"
-f "{title} {name}"

# Numbered: "#0 - Chapter 1.mp3"
-f "#{num} - {title}"

# With book name prefix: "anafem - 0 - Chapter 1.mp3"
-f "{name} - {num} - {title}"
```

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
  Average speed: 3.2MB/s
 + Completed in 4m 39s
```

## Project Structure

```
KVU_downloader/
├── pyproject.toml       # Project configuration
├── README.md            # This file
├── KVU_downloader.py    # Backward compatibility wrapper
└── kvu/                 # Main package
    ├── __init__.py      # Package exports
    ├── cli.py           # CLI entry point (argparse)
    ├── downloader.py    # Download manager with threading
    ├── parser.py        # HTML parser for book data
    ├── progress.py      # Rich progress utilities
    └── utils.py         # Helper functions
```

## Requirements

- Python 3.8+
- `requests` - HTTP library
- `rich` - Beautiful terminal output
- `beautifulsoup4` - HTML parsing for cover extraction
- `tqdm` - Fallback progress bar (optional)

## Backward Compatibility

The old `python KVU_downloader.py` command still works:

```bash
python KVU_downloader.py anafem -t 8
```

However, the recommended way is to use the new CLI:

```bash
kvu-download anafem -t 8
```

## License

MIT
