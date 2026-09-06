import unittest
from unittest.mock import patch
import os
import sys

from lar_os_nuclear_watcher import is_pid_alive

class TestNuclearWatcherPidLiveness(unittest.TestCase):

    @patch("lar_os_nuclear_watcher.sys.platform", "linux")
    @patch("lar_os_nuclear_watcher.os.kill")
    def test_is_pid_alive_linux_true(self, mock_kill):
        """Test that on non-Windows, if os.kill(pid, 0) succeeds, it returns True."""
        mock_kill.return_value = None
        self.assertTrue(is_pid_alive(12345))
        mock_kill.assert_called_once_with(12345, 0)

    @patch("lar_os_nuclear_watcher.sys.platform", "linux")
    @patch("lar_os_nuclear_watcher.os.kill")
    def test_is_pid_alive_linux_false(self, mock_kill):
        """Test that on non-Windows, if os.kill(pid, 0) raises OSError, it returns False."""
        mock_kill.side_effect = OSError("Process not found")
        self.assertFalse(is_pid_alive(12345))
        mock_kill.assert_called_once_with(12345, 0)

if __name__ == '__main__':
    unittest.main()
