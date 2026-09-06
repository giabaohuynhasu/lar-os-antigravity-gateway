import unittest
from unittest.mock import patch
import subprocess

from cloud_shell_bridge import get_session_info

class TestCloudShellBridge(unittest.TestCase):
    @patch("subprocess.check_output")
    def test_get_session_info_success(self, mock_check_output):
        # Mocking the output of successful tmux command
        mock_check_output.return_value = b"$0:1\n"

        result = get_session_info()

        self.assertEqual(result, {"session": "$0", "window": "1"})
        mock_check_output.assert_called_once_with(
            ["tmux", "display-message", "-p", "#{session_id}:#{window_index}"],
            stderr=subprocess.DEVNULL
        )

    @patch("subprocess.check_output")
    def test_get_session_info_failure(self, mock_check_output):
        # Mocking the failure of tmux command (e.g. not in tmux session)
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "tmux")

        result = get_session_info()

        self.assertEqual(result, {"session": "unknown", "window": "unknown"})
        mock_check_output.assert_called_once_with(
            ["tmux", "display-message", "-p", "#{session_id}:#{window_index}"],
            stderr=subprocess.DEVNULL
        )

    @patch("subprocess.check_output")
    def test_get_session_info_general_exception(self, mock_check_output):
        # Mocking general Exception (e.g., FileNotFoundError if tmux is missing)
        mock_check_output.side_effect = Exception("General error")

        result = get_session_info()

        self.assertEqual(result, {"session": "unknown", "window": "unknown"})
        mock_check_output.assert_called_once_with(
            ["tmux", "display-message", "-p", "#{session_id}:#{window_index}"],
            stderr=subprocess.DEVNULL
        )

if __name__ == "__main__":
    unittest.main()
