import unittest
from unittest.mock import patch, MagicMock
import json
from urllib.error import URLError

import agy_cli

class TestAgyCli(unittest.TestCase):
    @patch("agy_cli.urllib.request.urlopen")
    def test_check_gateway_health_online(self, mock_urlopen):
        mock_response = MagicMock()
        expected_data = {"status": "ONLINE", "pro_key_pool": {"active_keys": 5}}
        mock_response.read.return_value = json.dumps(expected_data).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        data = agy_cli.check_gateway_health()

        self.assertEqual(data["status"], "ONLINE")
        self.assertEqual(data["pro_key_pool"]["active_keys"], 5)
        mock_urlopen.assert_called_once()

    @patch("agy_cli.urllib.request.urlopen")
    def test_check_gateway_health_offline(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Connection refused")

        data = agy_cli.check_gateway_health()

        self.assertEqual(data["status"], "OFFLINE")
        self.assertIn("Connection refused", data["error"])

    @patch("agy_cli.urllib.request.urlopen")
    def test_check_opera_neon_health_online(self, mock_urlopen):
        mock_response = MagicMock()
        mock_tabs = [
            {"type": "page", "url": "https://claude.ai/chat"},
            {"type": "page", "url": "https://chatgpt.com/"},
            {"type": "page", "url": "https://mail.google.com/"},
            {"type": "background_page", "url": "chrome-extension://xyz"}
        ]
        mock_response.read.return_value = json.dumps(mock_tabs).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        data = agy_cli.check_opera_neon_health()

        self.assertEqual(data["status"], "ONLINE")
        self.assertEqual(data["tab_count"], 3)
        self.assertTrue(data["has_claude"])
        self.assertTrue(data["has_chatgpt"])
        self.assertTrue(data["has_gmail"])
        mock_urlopen.assert_called_once()

    @patch("agy_cli.urllib.request.urlopen")
    def test_check_opera_neon_health_offline(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Connection refused")

        data = agy_cli.check_opera_neon_health()

        self.assertEqual(data["status"], "OFFLINE")
        self.assertIn("Connection refused", data["error"])

if __name__ == "__main__":
    unittest.main()
