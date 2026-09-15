"""
Unit Tests for agy_cli
"""
import unittest
import json
import urllib.error
from unittest.mock import patch, MagicMock

from agy_cli import check_gateway_health, check_opera_neon_health

class TestAgyCli(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_check_gateway_health_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"status": "ONLINE"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = check_gateway_health()

        self.assertEqual(result, {"status": "ONLINE"})

    @patch("urllib.request.urlopen")
    def test_check_gateway_health_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        result = check_gateway_health()

        self.assertEqual(result["status"], "OFFLINE")
        self.assertIn("Connection refused", result["error"])

    @patch("urllib.request.urlopen")
    def test_check_opera_neon_health_success(self, mock_urlopen):
        tabs_data = [
            {"type": "page", "url": "https://claude.ai/chat/123"},
            {"type": "page", "url": "https://chatgpt.com/"},
            {"type": "page", "url": "https://mail.google.com/mail/u/0/"},
            {"type": "other", "url": "chrome-extension://abc"}
        ]
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(tabs_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = check_opera_neon_health()

        self.assertEqual(result["status"], "ONLINE")
        self.assertEqual(result["tab_count"], 3)
        self.assertTrue(result["has_claude"])
        self.assertTrue(result["has_chatgpt"])
        self.assertTrue(result["has_gmail"])

    @patch("urllib.request.urlopen")
    def test_check_opera_neon_health_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        result = check_opera_neon_health()

        self.assertEqual(result["status"], "OFFLINE")
        self.assertIn("Connection refused", result["error"])

if __name__ == "__main__":
    unittest.main()
