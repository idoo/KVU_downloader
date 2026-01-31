"""Rich console wrapper and UV-style progress display utilities."""

from typing import Optional, Any

# Try to import rich for UV-style progress, fallback to basic output
RICH_AVAILABLE = False
console: Optional[Any] = None
Panel: Optional[Any] = None

try:
    from rich.console import Console
    from rich.panel import Panel as RichPanel
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        DownloadColumn,
        TransferSpeedColumn,
        TimeRemainingColumn,
    )

    console = Console()
    Panel = RichPanel
    RICH_AVAILABLE = True
except ImportError:
    Progress = None  # type: ignore
    SpinnerColumn = None  # type: ignore
    TextColumn = None  # type: ignore
    BarColumn = None  # type: ignore
    DownloadColumn = None  # type: ignore
    TransferSpeedColumn = None  # type: ignore
    TimeRemainingColumn = None  # type: ignore


def print_uv_style(message: str, style: str = "info") -> None:
    """Print messages in UV style.

    Args:
        message: The message to print
        style: One of 'info', 'success', 'error', 'warning', 'header'
    """
    if RICH_AVAILABLE and console is not None:
        styles = {
            "info": f"[bold blue]  {message}[/]",
            "success": f"[bold green] + {message}[/]",
            "error": f"[bold red] ✗ {message}[/]",
            "warning": f"[bold yellow] ! {message}[/]",
            "header": f"[bold]{message}[/]",
        }
        console.print(styles.get(style, message))
    else:
        prefixes = {
            "info": "  ",
            "success": " + ",
            "error": " ✗ ",
            "warning": " ! ",
            "header": "",
        }
        print(f"{prefixes.get(style, '')}{message}")


def print_panel(content: str, title: str = "") -> None:
    """Print content in a bordered panel."""
    if RICH_AVAILABLE and console is not None and Panel is not None:
        console.print(Panel(content, title=title, border_style="blue"))
    else:
        if title:
            print(f"=== {title} ===")
        print(content)


def create_progress_context():
    """Create a rich Progress context manager or None if unavailable.

    Returns:
        A rich Progress instance configured for downloads, or None.
    """
    if not RICH_AVAILABLE:
        return None

    from rich.progress import (
        Progress as RichProgress,
        SpinnerColumn as RichSpinner,
        TextColumn as RichText,
        BarColumn as RichBar,
        DownloadColumn as RichDownload,
        TransferSpeedColumn as RichSpeed,
        TimeRemainingColumn as RichTime,
    )

    return RichProgress(
        RichSpinner(),
        RichText("[progress.description]{task.description}"),
        RichBar(bar_width=30),
        RichDownload(),
        RichSpeed(),
        RichTime(),
        console=console,
        transient=True,
    )
