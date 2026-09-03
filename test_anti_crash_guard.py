import unittest
from unittest.mock import patch, MagicMock
import json
from urllib.error import URLError

import anti_crash_guard

from pathlib import Path

class TestAntiCrashGuard(unittest.TestCase):
    @patch("anti_crash_guard.shutil.rmtree")
    @patch.object(Path, "iterdir")
    def test_clean_temp_sandboxes(self, mock_iterdir, mock_rmtree):
        # Create mock items
        mock_dir_temp = MagicMock()
        mock_dir_temp.is_dir.return_value = True
        mock_dir_temp.name = "temp_123"

        mock_dir_other = MagicMock()
        mock_dir_other.is_dir.return_value = True
        mock_dir_other.name = "other_dir"

        mock_file = MagicMock()
        mock_file.is_dir.return_value = False
        mock_file.name = "temp_file.txt"

        mock_iterdir.return_value = [mock_dir_temp, mock_dir_other, mock_file]

        deleted_count = anti_crash_guard.clean_temp_sandboxes()

        self.assertEqual(deleted_count, 1)
        mock_rmtree.assert_called_once_with(mock_dir_temp, ignore_errors=True)

    @patch("anti_crash_guard.urllib.request.urlopen")
    def test_check_gateway_health_success(self, mock_urlopen):
        mock_response = MagicMock()
        expected_data = {"status": "ok", "active_keys": 5}
        mock_response.read.return_value = json.dumps(expected_data).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        success, data = anti_crash_guard.check_gateway_health()

        self.assertTrue(success)
        self.assertEqual(data, expected_data)
        mock_urlopen.assert_called_once()
        
    @patch("anti_crash_guard.urllib.request.urlopen")
    def test_check_gateway_health_failure(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Connection refused")
        
        success, error_msg = anti_crash_guard.check_gateway_health()
        
        self.assertFalse(success)
        self.assertIn("Connection refused", error_msg)

    @patch("builtins.print")
    @patch("anti_crash_guard.shutil.disk_usage")
    @patch("anti_crash_guard.check_gateway_health")
    @patch("anti_crash_guard.clean_temp_sandboxes")
    def test_run_audit(self, mock_clean, mock_health, mock_disk, mock_print):
        mock_clean.return_value = 2
        mock_health.return_value = (True, {"active_keys": 10})
        # total, used, free
        mock_disk.return_value = (1000 * 2**30, 200 * 2**30, 800 * 2**30)
        
        anti_crash_guard.run_audit()
        
        mock_clean.assert_called_once()
        mock_health.assert_called_once()
        mock_disk.assert_called_with(str(anti_crash_guard.SCRATCH_DIR))
        self.assertTrue(mock_print.called)

        # Reset mocks to test failure branch of health check
        mock_health.reset_mock()
        mock_print.reset_mock()
        mock_health.return_value = (False, "Error")
        anti_crash_guard.run_audit()
        mock_health.assert_called_once()
        self.assertTrue(mock_print.called)

if __name__ == "__main__":
    unittest.main()
