"""
Tests for the main module functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the main module
import main


class TestMain:
    """Test cases for main module functions."""
    
    def test_main_with_no_args(self):
        """Test main function with no arguments."""
        with patch('sys.argv', ['main.py']):
            with patch('builtins.print') as mock_print:
                result = main.main()
                assert result == 0
                mock_print.assert_called()
    
    def test_main_with_input_file(self):
        """Test main function with input file argument."""
        test_args = ['main.py', '--input', 'test_input.txt']
        with patch('sys.argv', test_args):
            with patch('builtins.print') as mock_print:
                result = main.main()
                assert result == 0
                mock_print.assert_called()
    
    def test_main_with_verbose(self):
        """Test main function with verbose flag."""
        test_args = ['main.py', '--verbose']
        with patch('sys.argv', test_args):
            with patch('builtins.print') as mock_print:
                result = main.main()
                assert result == 0
                mock_print.assert_called()
    
    def test_main_with_output_file(self):
        """Test main function with output file argument."""
        test_args = ['main.py', '--output', 'test_output.txt']
        with patch('sys.argv', test_args):
            with patch('builtins.print') as mock_print:
                result = main.main()
                assert result == 0
                mock_print.assert_called()
    
    def test_main_with_all_args(self):
        """Test main function with all arguments."""
        test_args = [
            'main.py', 
            '--input', 'test_input.txt',
            '--output', 'test_output.txt',
            '--verbose'
        ]
        with patch('sys.argv', test_args):
            with patch('builtins.print') as mock_print:
                result = main.main()
                assert result == 0
                mock_print.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
