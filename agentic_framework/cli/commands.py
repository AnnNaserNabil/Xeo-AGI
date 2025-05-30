"""
CLI commands for the Xeo framework.
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .. import __version__, init, cleanup, get_llm_factory, Message, MessageRole
from ..core.plugins import get_plugin_manager, PluginType

app = typer.Typer(
    name="xeo",
    help="Xeo Framework Command Line Interface",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()

def print_header():
    """Print the Xeo CLI header."""
    console.print(
        Panel.fit(
            f"[bold blue]Xeo Framework[/] [dim]v{__version__}[/]",
            border_style="blue",
        ),
        "",
    )

@app.command()
def version():
    """Show the Xeo version."""
    print_header()
    console.print(f"Version: [bold]{__version__}[/]")

@app.command()
def chat(
    prompt: Optional[str] = typer.Argument(None, help="Initial prompt"),
    model: str = typer.Option(
        None,
        "--model", "-m",
        help="Model to use (default: from config)",
    ),
    provider: str = typer.Option(
        None,
        "--provider", "-p",
        help="LLM provider to use (default: from config)",
    ),
    temperature: float = typer.Option(
        0.7,
        "--temperature", "-t",
        min=0.0,
        max=2.0,
        help="Temperature for generation (0.0 to 2.0)",
    ),
):
    """Start an interactive chat session with the LLM."""
    print_header()
    
    # Initialize the framework
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Initializing Xeo...", total=None)
        init()
    
    try:
        # Get the LLM factory and create an instance
        llm_factory = get_llm_factory()
        
        with console.status("Initializing LLM...", spinner="dots"):
            llm = llm_factory.create_llm(
                provider_name=provider,
                model_name=model,
                temperature=temperature,
            )
        
        console.print("\n[bold]Xeo Chat[/] (type 'exit' or 'quit' to end)\n")
        
        # Start with the initial prompt if provided
        messages = []
        if prompt:
            messages.append(Message(role=MessageRole.USER, content=prompt))
            console.print(f"[bold]You:[/] {prompt}")
        
        # Main chat loop
        while True:
            try:
                # Get user input
                try:
                    user_input = console.input("[bold]You:[/] ").strip()
                except (EOFError, KeyboardInterrupt):
                    console.print("\nGoodbye!")
                    break
                
                if user_input.lower() in ("exit", "quit"):
                    console.print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Add user message to history
                messages.append(Message(role=MessageRole.USER, content=user_input))
                
                # Get assistant response
                with console.status("Thinking...", spinner="dots"):
                    response = asyncio.run(llm.chat(messages))
                    assistant_message = response.content
                    messages.append(Message(role=MessageRole.ASSISTANT, content=assistant_message))
                
                # Print assistant response
                console.print(f"[bold]Assistant:[/] {assistant_message}")
                
            except Exception as e:
                console.print(f"[red]Error:[/] {str(e)}")
    
    finally:
        # Clean up resources
        cleanup()

@app.command()
def plugins():
    """List all available plugins."""
    print_header()
    
    # Initialize the framework to load plugins
    init()
    
    try:
        plugin_manager = get_plugin_manager()
        
        # Create a table to display plugins
        table = Table(
            title="Installed Plugins",
            show_header=True,
            header_style="bold blue",
            expand=True,
        )
        
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Version", style="green")
        table.add_column("Description")
        
        # Add plugins to the table
        for name, plugin in plugin_manager._plugins.items():
            info = plugin.plugin_info
            table.add_row(
                info.name,
                info.type.value if info.type else "N/A",
                info.version,
                info.description or "No description available",
            )
        
        console.print(table)
    
    finally:
        cleanup()

@app.command()
def config():
    """Show the current configuration."""
    print_header()
    
    from ..config import get_settings
    from ..config.providers import get_llm_config
    
    settings = get_settings()
    llm_config = get_llm_config()
    
    # Display core settings
    console.print("[bold blue]Core Settings:[/]")
    core_table = Table(show_header=False, box=None, show_edge=False)
    core_table.add_column(style="cyan", no_wrap=True)
    core_table.add_column()
    
    core_table.add_row("Debug Mode:", "Enabled" if settings.DEBUG else "Disabled")
    core_table.add_row("Log Level:", settings.LOG_LEVEL)
    core_table.add_row("Data Directory:", str(settings.DATA_DIR))
    core_table.add_row("Cache Directory:", str(settings.CACHE_DIR))
    
    console.print(core_table)
    console.print()
    
    # Display LLM settings
    console.print("[bold blue]LLM Configuration:[/]")
    llm_table = Table(
        show_header=True,
        header_style="bold blue",
        box=None,
    )
    llm_table.add_column("Provider", style="cyan")
    llm_table.add_column("Enabled")
    llm_table.add_column("Default Model")
    llm_table.add_column("Priority")
    
    for provider_name, provider_config in llm_config.providers.items():
        llm_table.add_row(
            provider_name,
            "✓" if provider_config.enabled else "✗",
            provider_config.config.get("default_model", "N/A"),
            str(provider_config.priority),
        )
    
    console.print(llm_table)

if __name__ == "__main__":
    app()
