"""
Xeo Command Line Interface (CLI).

This module provides a command-line interface for interacting with the Xeo framework.
"""

__version__ = "0.2.0"
__all__ = ["main"]

def main():
    """Entry point for the Xeo CLI."""
    import typer
    from .commands import app
    
    app()

if __name__ == "__main__":
    main()
