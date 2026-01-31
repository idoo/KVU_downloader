"""HTML parser for extracting book data from knigavuhe.org."""

import json
import re
from typing import Optional
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from .utils import extract_ending
from .progress import print_uv_style


@dataclass
class BookInfo:
    """Container for parsed book information."""

    title: Optional[str] = None
    author: Optional[str] = None
    cover_url: Optional[str] = None
    tracks: list = None  # type: ignore

    def __post_init__(self):
        if self.tracks is None:
            self.tracks = []


class BookParser:
    """Parser for knigavuhe.org book pages.

    Extracts book metadata, cover image URL, and audio track URLs.
    """

    BASE_URL = "https://knigavuhe.org/book/"

    def __init__(self, url_or_ending: str):
        """Initialize parser with a book URL or ending.

        Args:
            url_or_ending: Full URL or just the book ending (e.g., 'anafem')
        """
        self._ending = extract_ending(url_or_ending)
        self._html: Optional[str] = None
        self._soup: Optional[BeautifulSoup] = None
        self._info: Optional[BookInfo] = None

    @property
    def ending(self) -> str:
        """Book URL ending/slug."""
        return self._ending

    @property
    def url(self) -> str:
        """Full book URL."""
        return f"{self.BASE_URL}{self._ending}/"

    @property
    def html(self) -> Optional[str]:
        """Raw HTML content (None if not fetched)."""
        return self._html

    def fetch(self) -> bool:
        """Fetch the book page from knigavuhe.org.

        Returns:
            True if fetch was successful, False otherwise.
        """
        print_uv_style(f"Fetching book data from {self.url}", "header")

        try:
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print_uv_style(f"Connection error: {e}", "error")
            return False

        if response.status_code != 200:
            print_uv_style(f"Bad URL (status {response.status_code})", "error")
            return False

        self._html = response.text
        self._soup = BeautifulSoup(self._html, "html.parser")
        self._parse()
        return True

    def _parse(self) -> None:
        """Parse all book information from HTML."""
        self._info = BookInfo(
            title=self._extract_title(),
            author=self._extract_author(),
            cover_url=self._extract_cover_url(),
            tracks=self._extract_tracks(),
        )

    def _extract_title(self) -> Optional[str]:
        """Extract book title from HTML."""
        if not self._soup:
            return None

        # Try h1.book_title_name first
        title_el = self._soup.select_one("h1.book_title_name span")
        if title_el:
            return title_el.get_text(strip=True)

        # Fallback to just h1.book_title_name
        title_el = self._soup.select_one("h1.book_title_name")
        if title_el:
            return title_el.get_text(strip=True)

        # Try meta tag
        meta = self._soup.select_one('meta[property="og:title"]')
        if meta:
            return meta.get("content")

        return None

    def _extract_author(self) -> Optional[str]:
        """Extract author name from HTML."""
        if not self._soup:
            return None

        # Try span.book_title_elem with author link
        author_el = self._soup.select_one("span.book_title_elem a")
        if author_el:
            return author_el.get_text(strip=True)

        # Try alternative selector
        author_el = self._soup.select_one(".book_title_author a")
        if author_el:
            return author_el.get_text(strip=True)

        return None

    def _extract_cover_url(self) -> Optional[str]:
        """Extract cover image URL from HTML.

        Uses the CSS selector:
        div.book_cover > img
        """
        if not self._soup:
            return None

        # Primary selector based on user's CSS path
        img = self._soup.select_one("div.book_cover > img")
        if img:
            # Try src first, then data-src (lazy loading)
            url = img.get("src") or img.get("data-src")
            if url:
                # Handle relative URLs
                if url.startswith("//"):
                    return "https:" + url
                elif url.startswith("/"):
                    return "https://knigavuhe.org" + url
                return url

        # Fallback: try og:image meta tag
        meta = self._soup.select_one('meta[property="og:image"]')
        if meta:
            return meta.get("content")

        return None

    def _extract_tracks(self) -> list:
        """Extract audio track URLs and titles from JavaScript.

        Parses the BookPlayer JavaScript initialization to get track data.
        """
        if not self._html:
            return []

        # Find the BookPlayer initialization
        match = re.findall(
            r"var player = new BookPlayer\([0-9]{1,}, \[.{1,}]", self._html
        )
        if not match:
            return []

        # Extract JSON array
        json_str = match[0][match[0].find("[") : match[0].find("]")] + "]"

        try:
            tracks = json.loads(json_str, strict=False)
            return tracks
        except json.JSONDecodeError:
            print_uv_style("Failed to parse track data", "error")
            return []

    def get_title(self) -> Optional[str]:
        """Get parsed book title."""
        return self._info.title if self._info else None

    def get_author(self) -> Optional[str]:
        """Get parsed author name."""
        return self._info.author if self._info else None

    def get_cover_url(self) -> Optional[str]:
        """Get parsed cover image URL."""
        return self._info.cover_url if self._info else None

    def get_tracks(self) -> list:
        """Get parsed audio tracks."""
        return self._info.tracks if self._info else []

    def get_info(self) -> Optional[BookInfo]:
        """Get all parsed book information."""
        return self._info
