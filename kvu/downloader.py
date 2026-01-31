"""Download manager with threading and progress tracking."""

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from typing import Optional, Tuple, List, Any, Union

import requests

from .utils import format_size, format_time, get_file_extension
from .progress import print_uv_style, create_progress_context, RICH_AVAILABLE


class DownloadStats:
    """Thread-safe download statistics tracker."""

    def __init__(self):
        self.lock = threading.Lock()
        self.completed = 0
        self.failed = 0
        self.total_bytes = 0
        self.start_time: Optional[float] = None
        self.results: List[Tuple] = []

    def start(self) -> None:
        """Mark the start of download session."""
        self.start_time = time.time()

    def add_success(self, filename: str, size_bytes: int) -> None:
        """Record a successful download."""
        with self.lock:
            self.completed += 1
            self.total_bytes += size_bytes
            self.results.append(("success", filename))

    def add_failure(self, filename: str, error: str) -> None:
        """Record a failed download."""
        with self.lock:
            self.failed += 1
            self.results.append(("failed", filename, str(error)))

    def elapsed(self) -> float:
        """Get elapsed time since start."""
        return time.time() - self.start_time if self.start_time else 0

    def print_summary(self) -> None:
        """Print download summary in UV style."""
        elapsed = self.elapsed()

        print()
        if self.completed > 0:
            print_uv_style(
                f"Downloaded {self.completed} files ({format_size(self.total_bytes)}) "
                f"in {format_time(elapsed)}",
                "success",
            )
            if elapsed > 0:
                speed = self.total_bytes / elapsed
                print_uv_style(f"Average speed: {format_size(speed)}/s", "info")

        if self.failed > 0:
            print_uv_style(f"{self.failed} files failed to download", "error")
            for result in self.results:
                if result[0] == "failed":
                    print_uv_style(f"  {result[1]}: {result[2]}", "error")


class Downloader:
    """Manages file downloads with threading and progress tracking."""

    def __init__(
        self,
        output_dir: str,
        threads: int = 4,
        name_format: str = "{title} {name}",
    ):
        """Initialize downloader.

        Args:
            output_dir: Directory to save downloaded files
            threads: Number of concurrent download threads
            name_format: Format string for audio file names
        """
        self.output_dir = output_dir
        self.threads = threads
        self.name_format = name_format
        self._stats = DownloadStats()

    @property
    def stats(self) -> DownloadStats:
        """Get download statistics."""
        return self._stats

    def ensure_output_dir(self) -> bool:
        """Create output directory if it doesn't exist.

        Returns:
            True if directory exists or was created, False on error.
        """
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            return True
        except OSError as e:
            print_uv_style(f"Cannot create directory: {e}", "error")
            return False

    def download_file(
        self,
        url: str,
        filename: str,
        progress: Optional[Any] = None,
        retries: int = 3,
    ) -> Tuple[str, str, Union[int, str]]:
        """Download a single file.

        Args:
            url: URL to download
            filename: Local filename to save as
            progress: Rich progress instance for tracking (optional)
            retries: Number of retry attempts

        Returns:
            Tuple of (status, filename, bytes_downloaded or error_message)
        """
        file_path = os.path.join(self.output_dir, filename)
        task_id = None

        for attempt in range(retries):
            try:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))

                if RICH_AVAILABLE and progress:
                    display_name = (
                        filename[:40] + "..." if len(filename) > 40 else filename
                    )
                    task_id = progress.add_task(
                        f"[cyan]{display_name}",
                        total=total_size if total_size > 0 else None,
                    )

                downloaded = 0
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024 * 64):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            if RICH_AVAILABLE and progress and task_id is not None:
                                progress.update(task_id, completed=downloaded)

                if RICH_AVAILABLE and progress and task_id is not None:
                    progress.remove_task(task_id)

                return ("success", filename, downloaded)

            except Exception as e:
                if task_id is not None and RICH_AVAILABLE and progress:
                    try:
                        progress.remove_task(task_id)
                    except Exception:
                        pass

                if attempt == retries - 1:
                    return ("failed", filename, str(e))
                time.sleep(2)

        return ("failed", filename, "Unknown error")

    def download_cover(self, cover_url: str) -> bool:
        """Download book cover image.

        Args:
            cover_url: URL of the cover image

        Returns:
            True if download was successful, False otherwise.
        """
        if not cover_url:
            print_uv_style("No cover image found", "warning")
            return False

        ext = get_file_extension(cover_url)
        filename = f"cover{ext}"

        print_uv_style(f"Downloading cover image...", "info")

        try:
            response = requests.get(cover_url, timeout=30)
            response.raise_for_status()

            file_path = os.path.join(self.output_dir, filename)
            with open(file_path, "wb") as f:
                f.write(response.content)

            size = len(response.content)
            print_uv_style(f"Downloaded {filename} ({format_size(size)})", "success")
            return True

        except Exception as e:
            print_uv_style(f"Failed to download cover: {e}", "error")
            return False

    def download_tracks(self, tracks: list) -> None:
        """Download all audio tracks.

        Args:
            tracks: List of track dictionaries with 'url' and 'title' keys
        """
        if not tracks:
            print_uv_style("No tracks to download", "warning")
            return

        total_tracks = len(tracks)
        print_uv_style(f"Resolved {total_tracks} tracks", "info")
        print_uv_style(
            f"Downloading {total_tracks} files using {self.threads} threads",
            "header",
        )

        self._stats.start()

        if RICH_AVAILABLE:
            self._download_with_rich_progress(tracks)
        else:
            self._download_with_tqdm(tracks)

        self._stats.print_summary()

    def _download_with_rich_progress(self, tracks: list) -> None:
        """Download tracks with rich progress display."""
        progress = create_progress_context()
        if progress is None:
            self._download_with_tqdm(tracks)
            return

        total_tracks = len(tracks)

        with progress:
            overall_task = progress.add_task(
                f"[bold green]Downloading {total_tracks} tracks...",
                total=total_tracks,
            )

            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                download_fn = partial(
                    self._download_track_task,
                    progress=progress,
                )

                futures = {
                    executor.submit(download_fn, idx, track): (idx, track)
                    for idx, track in enumerate(tracks)
                }

                for future in as_completed(futures):
                    future.result()
                    progress.update(overall_task, advance=1)

    def _download_with_tqdm(self, tracks: list) -> None:
        """Download tracks with tqdm progress (fallback)."""
        try:
            from tqdm import tqdm
        except ImportError:
            print_uv_style("Neither rich nor tqdm available for progress", "warning")
            tqdm = None

        total_tracks = len(tracks)

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            download_fn = partial(self._download_track_task, progress=None)

            futures = [
                executor.submit(download_fn, idx, track)
                for idx, track in enumerate(tracks)
            ]

            if tqdm:
                for future in tqdm(
                    as_completed(futures), total=total_tracks, desc="Downloading"
                ):
                    future.result()
            else:
                for future in as_completed(futures):
                    future.result()

    def _download_track_task(
        self,
        idx: int,
        track: dict,
        progress: Optional[Any] = None,
    ) -> Tuple[str, str, Union[int, str]]:
        """Download a single track (for use with ThreadPoolExecutor)."""
        url = track.get("url", "")
        title = track.get("title", f"track_{idx}")

        filename = self.name_format.format(
            name=os.path.basename(self.output_dir),
            title=title,
            num=idx,
        )
        filename = f"{filename}.mp3"

        result = self.download_file(url, filename, progress)

        if result[0] == "success":
            self._stats.add_success(result[1], int(result[2]))
        else:
            self._stats.add_failure(result[1], str(result[2]))

        return result
