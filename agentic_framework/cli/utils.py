"""
Utility functions for the Xeo CLI.
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, List, Union

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt, IntPrompt
from rich.table import Table

console = Console()

def print_error(message: str) -> None:
    """Print an error message.
    
    Args:
        message: The error message to display
    """
    console.print(f"[red]Error:[/] {message}")

def print_success(message: str) -> None:
    """Print a success message.
    
    Args:
        message: The success message to display
    """
    console.print(f"[green]✓[/] {message}")

def print_warning(message: str) -> None:
    """Print a warning message.
    
    Args:
        message: The warning message to display
    """
    console.print(f"[yellow]![/] {message}")

def print_info(message: str) -> None:
    """Print an informational message.
    
    Args:
        message: The info message to display
    """
    console.print(f"[blue]i[/] {message}")

def confirm(question: str, default: bool = False) -> bool:
    """Ask for confirmation.
    
    Args:
        question: The question to ask
        default: Default value if user just presses Enter
        
    Returns:
        bool: True if confirmed, False otherwise
    """
    return Confirm.ask(f"[yellow]?[/] {question}", default=default)

def ask(question: str, default: str = "") -> str:
    """Ask for user input.
    
    Args:
        question: The question to ask
        default: Default value if user just presses Enter
        
    Returns:
        str: User input or default value
    """
    return Prompt.ask(f"[blue]?[/] {question}", default=default)

def ask_int(question: str, default: int = 0) -> int:
    """Ask for an integer input.
    
    Args:
        question: The question to ask
        default: Default value if user just presses Enter
        
    Returns:
        int: User input or default value
    """
    return IntPrompt.ask(f"[blue]?[/] {question}", default=default)

def print_json(data: Any, title: Optional[str] = None) -> None:
    """Print data as formatted JSON.
    
    Args:
        data: The data to print as JSON
        title: Optional title for the JSON output
    """
    import json
    from pygments import highlight
    from pygments.lexers import JsonLexer
    from pygments.formatters import TerminalFormatter
    
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    
    if title:
        console.print(f"[bold]{title}:[/]")
    
    # Use pygments for syntax highlighting if available
    try:
        console.print(highlight(json_str, JsonLexer(), TerminalFormatter()))
    except ImportError:
        console.print_json(json_str)

def create_table(
    title: str,
    columns: List[Dict[str, Any]],
    data: List[Any],
    show_header: bool = True,
    border_style: str = "blue",
    expand: bool = False,
) -> None:
    """Create and print a rich table.
    
    Args:
        title: Table title
        columns: List of column definitions with 'header' and 'style' keys
        data: List of data rows (each row is a list of values)
        show_header: Whether to show the header row
        border_style: Style for the table border
        expand: Whether to expand the table to full width
    """
    table = Table(
        title=title,
        show_header=show_header,
        header_style=f"bold {border_style}",
        border_style=border_style,
        expand=expand,
    )
    
    # Add columns
    for col in columns:
        table.add_column(
            col["header"],
            style=col.get("style", ""),
            no_wrap=col.get("no_wrap", False),
            justify=col.get("justify", "left"),
        )
    
    # Add rows
    for row in data:
        table.add_row(*[str(cell) for cell in row])
    
    console.print(table)

def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists.
    
    Args:
        path: Path to the directory
        
    Returns:
        Path: The path object for the directory
    """
    path = Path(path).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_config_dir() -> Path:
    """Get the Xeo configuration directory.
    
    Returns:
        Path: Path to the Xeo config directory
    """
    if os.name == "nt":  # Windows
        base_dir = Path(os.environ.get("APPDATA", ""))
    else:  # Unix-like
        base_dir = Path.home() / ".config"
    
    config_dir = base_dir / "xeo"
    return ensure_directory(config_dir)
