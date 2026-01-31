"""Utility functions for URL parsing and formatting."""


def extract_ending(url_or_ending: str) -> str:
    """Extract book ending from full URL or return as-is if already an ending.

    Examples:
        >>> extract_ending("https://knigavuhe.org/book/zapiski-okhotnika/")
        'zapiski-okhotnika'
        >>> extract_ending("anafem")
        'anafem'
    """
    url_or_ending = url_or_ending.strip().rstrip("/")

    # Check if it's a full URL
    if url_or_ending.startswith("http://") or url_or_ending.startswith("https://"):
        # Extract the ending from URL like https://knigavuhe.org/book/zapiski-okhotnika/
        if "/book/" in url_or_ending:
            parts = url_or_ending.split("/book/")
            if len(parts) > 1:
                return parts[1].strip("/")
        # Fallback: take the last path segment
        return url_or_ending.split("/")[-1]

    return url_or_ending


def format_size(size_bytes: float) -> str:
    """Format bytes to human readable string.

    Examples:
        >>> format_size(1024)
        '1.0KB'
        >>> format_size(1048576)
        '1.0MB'
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


def format_time(seconds: float) -> str:
    """Format seconds to human readable string.

    Examples:
        >>> format_time(0.5)
        '500ms'
        >>> format_time(65)
        '1m 5s'
    """
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.0f}s"


def get_file_extension(url: str) -> str:
    """Extract file extension from URL.

    Examples:
        >>> get_file_extension("https://example.com/cover.jpg?v=1")
        '.jpg'
        >>> get_file_extension("https://example.com/image.webp")
        '.webp'
    """
    # Remove query parameters
    path = url.split("?")[0]
    # Get the last part after the last dot
    if "." in path.split("/")[-1]:
        ext = "." + path.split(".")[-1].lower()
        # Validate it's a reasonable extension
        if len(ext) <= 5 and ext.isascii():
            return ext
    return ".jpg"  # Default fallback
