"""
Tests for the Xeo CLI utilities.
"""
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from rich.console import Console

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from xeo.cli.utils import (
    print_error,
    print_success,
    print_warning,
    print_info,
    confirm,
    ask,
    ask_int,
    print_json,
    create_table,
    ensure_directory,
    get_config_dir
)

class TestCLIUtils:
    """Test suite for CLI utilities."""
    
    def test_print_functions(self, capsys):
        """Test the print utility functions."""
        # Test print_error
        print_error("Test error")
        captured = capsys.readouterr()
        assert "Test error" in captured.err
        
        # Test print_success
        print_success("Test success")
        captured = capsys.readouterr()
        assert "Test success" in captured.out
        
        # Test print_warning
        print_warning("Test warning")
        captured = capsys.readouterr()
        assert "Test warning" in captured.out
        
        # Test print_info
        print_info("Test info")
        captured = capsys.readouterr()
        assert "Test info" in captured.out
    
    @patch("xeo.cli.utils.Confirm.ask")
    def test_confirm(self, mock_ask):
        """Test the confirm function."""
        mock_ask.return_value = True
        assert confirm("Continue?") is True
        mock_ask.assert_called_once()
    
    @patch("xeo.cli.utils.Prompt.ask")
    def test_ask(self, mock_ask):
        """Test the ask function."""
        mock_ask.return_value = "test input"
        assert ask("Enter something:") == "test input"
        mock_ask.assert_called_once()
    
    @patch("xeo.cli.utils.IntPrompt.ask")
    def test_ask_int(self, mock_ask):
        """Test the ask_int function."""
        mock_ask.return_value = 42
        assert ask_int("Enter a number:") == 42
        mock_ask.assert_called_once()
    
    def test_print_json(self, capsys):
        """Test the print_json function."""
        test_data = {"key": "value", "number": 42}
        print_json(test_data)
        captured = capsys.readouterr()
        assert "key" in captured.out
        assert "value" in captured.out
        assert "42" in captured.out
    
    def test_create_table(self, capsys):
        """Test the create_table function."""
        columns = [
            {"header": "Name", "style": "cyan"},
            {"header": "Value", "style": "green"}
        ]
        data = [
            ["Test", "123"],
            ["Another", "456"]
        ]
        create_table("Test Table", columns, data)
        captured = capsys.readouterr()
        assert "Test Table" in captured.out
        assert "Name" in captured.out
        assert "Value" in captured.out
        assert "Test" in captured.out
        assert "Another" in captured.out
    
    def test_ensure_directory(self, tmp_path):
        """Test the ensure_directory function."""
        test_dir = tmp_path / "test_dir"
        assert not test_dir.exists()
        
        result = ensure_directory(test_dir)
        assert result.exists()
        assert result == test_dir
        
        # Test with existing directory
        result = ensure_directory(test_dir)
        assert result.exists()
    
    @patch("os.name", "posix")
    @patch.dict(os.environ, {}, clear=True)
    def test_get_config_dir_unix(self):
        """Test get_config_dir on Unix-like systems."""
        with patch("pathlib.Path.home", return_value=Path("/home/test"):
            config_dir = get_config_dir()
            assert str(config_dir) == "/home/test/.config/xeo"
    
    @patch("os.name", "nt")
    @patch.dict(os.environ, {"APPDATA": "C:\\Users\\test\\AppData\\Roaming"}, clear=True)
    def test_get_config_dir_windows(self):
        """Test get_config_dir on Windows."""
        config_dir = get_config_dir()
        assert str(config_dir) == r"C:\Users\test\AppData\Roaming\xeo"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
