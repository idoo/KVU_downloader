"""KVU Downloader - Audiobook downloader for knigavuhe.org."""

__version__ = "2.1.0"

from .cli import main
from .downloader import Downloader, DownloadStats
from .parser import BookParser

__all__ = ["main", "Downloader", "DownloadStats", "BookParser", "__version__"]
