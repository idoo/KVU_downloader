"""Command-line interface for KVU Downloader."""

import argparse
import sys
import time

from . import __version__
from .parser import BookParser
from .downloader import Downloader
from .progress import print_uv_style, print_panel
from .utils import format_time


USAGE_EXAMPLES = """
Examples:
  kvu-download https://knigavuhe.org/book/zapiski-okhotnika/
  kvu-download anafem -t 8
  kvu-download anafem -f "#{num} - {title}"
  kvu-download anafem --cover-only
  kvu-download anafem -o ~/audiobooks/

Format variables for -f/--format:
  {title}  - Track title
  {num}    - Track number (0-indexed)
  {name}   - Book ending/slug
"""


def parse_args(args=None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Arguments to parse (defaults to sys.argv)

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        prog="kvu-download",
        description="Audiobook downloader for knigavuhe.org with UV-style progress display",
        epilog=USAGE_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "url",
        nargs="?",
        help="Book URL or ending (e.g., 'anafem' or full URL)",
    )

    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=4,
        metavar="N",
        help="Number of download threads (default: 4)",
    )

    parser.add_argument(
        "-f",
        "--format",
        default="{title} {name}",
        metavar="FMT",
        help='Filename format (default: "{title} {name}")',
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        help="Output directory (default: book ending)",
    )

    parser.add_argument(
        "--no-cover",
        action="store_true",
        help="Skip cover image download",
    )

    parser.add_argument(
        "--cover-only",
        action="store_true",
        help="Only download cover image",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parsed = parser.parse_args(args)

    # Show help if no URL provided
    if not parsed.url:
        parser.print_help()
        sys.exit(0)

    return parsed


def main(args=None) -> int:
    """Main entry point for KVU Downloader.

    Args:
        args: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parsed = parse_args(args)
    start_time = time.time()

    # 1. Parse book page
    parser = BookParser(parsed.url)
    if not parser.fetch():
        return 1

    # 2. Display book info
    title = parser.get_title()
    author = parser.get_author()

    if title:
        print_uv_style(f"Book: {title}", "header")
    if author:
        print_uv_style(f"Author: {author}", "info")

    # 3. Setup downloader
    output_dir = parsed.output or parser.ending
    downloader = Downloader(
        output_dir=output_dir,
        threads=parsed.threads,
        name_format=parsed.format,
    )

    if not downloader.ensure_output_dir():
        return 1

    # 4. Download cover first (unless --no-cover)
    if not parsed.no_cover:
        cover_url = parser.get_cover_url()
        if cover_url:
            downloader.download_cover(cover_url)
        else:
            print_uv_style("No cover image found", "warning")

    # 5. Download tracks (unless --cover-only)
    if not parsed.cover_only:
        tracks = parser.get_tracks()
        if tracks:
            downloader.download_tracks(tracks)
        else:
            print_uv_style("No audio tracks found", "error")
            return 1

    # 6. Print completion time
    total_time = time.time() - start_time
    print_uv_style(f"Completed in {format_time(total_time)}", "success")

    return 0


if __name__ == "__main__":
    sys.exit(main())
