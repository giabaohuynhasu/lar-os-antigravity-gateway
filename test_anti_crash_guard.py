import unittest
from unittest.mock import patch, MagicMock
import json
from urllib.error import URLError
import tempfile
import os

import anti_crash_guard

from pathlib import Path

class TestAntiCrashGuard(unittest.TestCase):
    def test_clean_temp_sandboxes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a mock sandbox structure
            (temp_path / "temp_123").mkdir()
            (temp_path / "temp_456").mkdir()
            (temp_path / "other_dir").mkdir()
            (temp_path / "temp_file.txt").touch()

            with patch("anti_crash_guard.SANDBOX_DIR", temp_path):
                deleted_count = anti_crash_guard.clean_temp_sandboxes()

            self.assertEqual(deleted_count, 2)
            self.assertFalse((temp_path / "temp_123").exists())
            self.assertFalse((temp_path / "temp_456").exists())
            self.assertTrue((temp_path / "other_dir").exists())
            self.assertTrue((temp_path / "temp_file.txt").exists())

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
        mock_disk.assert_called_with(str(anti_crash_guard.SANDBOX_DIR))
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
