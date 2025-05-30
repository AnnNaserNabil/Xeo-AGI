#!/usr/bin/env python3
"""
Setup script for the Xeo CLI.

This script ensures all required dependencies are installed and sets up the environment.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

# Required packages for the CLI
REQUIRED_PACKAGES = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "python-dotenv>=1.0.0",
]

def check_python_version():
    """Check if the Python version is supported."""
    if sys.version_info < (3, 8):
        print("Error: Xeo requires Python 3.8 or higher.")
        sys.exit(1)

def check_installed(package_name):
    """Check if a package is installed."""
    try:
        __import__(package_name.split('>=')[0].split('[')[0])
        return True
    except ImportError:
        return False

def install_packages(packages):
    """Install required packages."""
    import subprocess
    import sys
    
    for package in packages:
        if not check_installed(package):
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def setup_environment():
    """Set up the environment variables."""
    env_file = Path(".env")
    if not env_file.exists():
        print("Setting up environment variables...")
        shutil.copy(".env.example", ".env")
        print("Created .env file. Please update it with your API keys.")

def main():
    """Main setup function."""
    print("Setting up Xeo CLI...")
    
    # Check Python version
    check_python_version()
    
    # Install required packages
    print("Checking dependencies...")
    install_packages(REQUIRED_PACKAGES)
    
    # Set up environment
    setup_environment()
    
    # Make CLI script executable (Unix-like systems)
    if os.name != 'nt':
        cli_script = Path(__file__).parent / "xeo" / "cli" / "main.py"
        if cli_script.exists():
            cli_script.chmod(0o755)
    
    print("\n✅ Setup complete!")
    print("\nTo get started, run:")
    print("  xeo --help")
    print("\nMake sure to update your .env file with your API keys.")

if __name__ == "__main__":
    main()
