import unittest
from unittest.mock import patch, MagicMock
import psutil
from lar_os_gateway import get_windows_process_creation_time

class TestGetWindowsProcessCreationTime(unittest.TestCase):
    @patch('psutil.Process')
    def test_psutil_success(self, mock_process_cls):
        """Should return creation time from psutil if available"""
        mock_process = MagicMock()
        mock_process.create_time.return_value = 12345.6
        mock_process_cls.return_value = mock_process

        # Test success path
        self.assertEqual(get_windows_process_creation_time(1000), 12345.6)
        mock_process_cls.assert_called_with(1000)

    @patch('psutil.Process')
    def test_psutil_no_such_process(self, mock_process_cls):
        """Should return 0.0 if process does not exist in psutil"""
        mock_process_cls.side_effect = psutil.NoSuchProcess(pid=1000)

        self.assertEqual(get_windows_process_creation_time(1000), 0.0)

if __name__ == '__main__':
    unittest.main()
