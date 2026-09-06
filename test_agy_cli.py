import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Import the module to test
import agy_cli

class TestAgyCli(unittest.TestCase):
    def test_has_stdin_data_none(self):
        """Test when sys.stdin is None."""
        with patch('sys.stdin', None):
            self.assertFalse(agy_cli.has_stdin_data())

    def test_has_stdin_data_isatty(self):
        """Test when sys.stdin.isatty() is True (terminal interaction)."""
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = True
        with patch('sys.stdin', mock_stdin):
            self.assertFalse(agy_cli.has_stdin_data())

    def test_has_stdin_data_win32_success(self):
        """Test when on win32 and there is data available in stdin."""
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = False
        mock_stdin.fileno.return_value = 1

        with patch('sys.stdin', mock_stdin), \
             patch('sys.platform', 'win32'), \
             patch.dict('sys.modules', {}):

            # Create a mock for msvcrt
            mock_msvcrt = MagicMock()
            mock_msvcrt.get_osfhandle.return_value = 12345

            # Create mocks for ctypes
            mock_ctypes = MagicMock()

            # Mock wintypes
            mock_wintypes = MagicMock()
            mock_avail = MagicMock()
            mock_avail.value = 5 # Data available
            mock_wintypes.DWORD.return_value = mock_avail
            mock_wintypes.HANDLE = MagicMock()

            mock_ctypes.wintypes = mock_wintypes
            mock_ctypes.windll.kernel32.PeekNamedPipe.return_value = 1 # Success
            mock_ctypes.byref = MagicMock()

            # Put them in sys.modules so the local imports work
            sys.modules['msvcrt'] = mock_msvcrt
            sys.modules['ctypes'] = mock_ctypes

            self.assertTrue(agy_cli.has_stdin_data())

            # Test no data
            mock_avail.value = 0
            self.assertFalse(agy_cli.has_stdin_data())

            # Test failure of PeekNamedPipe
            mock_ctypes.windll.kernel32.PeekNamedPipe.return_value = 0
            mock_avail.value = 5
            self.assertFalse(agy_cli.has_stdin_data())

    def test_has_stdin_data_win32_exception(self):
        """Test when on win32 but an exception occurs (e.g. invalid handle)."""
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = False
        mock_stdin.fileno.return_value = 1

        with patch('sys.stdin', mock_stdin), \
             patch('sys.platform', 'win32'), \
             patch.dict('sys.modules', {}):

            mock_msvcrt = MagicMock()
            mock_msvcrt.get_osfhandle.side_effect = Exception("invalid handle error")
            sys.modules['msvcrt'] = mock_msvcrt

            self.assertFalse(agy_cli.has_stdin_data())

    def test_has_stdin_data_other_os(self):
        """Test when on an OS other than win32."""
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = False

        with patch('sys.stdin', mock_stdin), \
             patch('sys.platform', 'linux'):
             self.assertFalse(agy_cli.has_stdin_data())

if __name__ == '__main__':
    unittest.main()
