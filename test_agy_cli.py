import unittest
from unittest.mock import patch, MagicMock
import json
import urllib.error

import agy_cli

class TestAgyCli(unittest.TestCase):

    @patch("agy_cli.urllib.request.urlopen")
    def test_check_gateway_health_success(self, mock_urlopen):
        mock_response = MagicMock()
        expected_data = {"status": "ONLINE", "active_keys": 5}
        mock_response.read.return_value = json.dumps(expected_data).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = agy_cli.check_gateway_health()

        self.assertEqual(result, expected_data)
        mock_urlopen.assert_called_once()

    @patch("agy_cli.urllib.request.urlopen")
    def test_check_gateway_health_failure(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused")

        result = agy_cli.check_gateway_health()

        self.assertEqual(result["status"], "OFFLINE")
        self.assertEqual(result["error"], "Connection refused")

    @patch("agy_cli.urllib.request.urlopen")
    def test_check_opera_neon_health_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_tabs = [
            {"type": "page", "url": "https://claude.ai/chat/123"},
            {"type": "page", "url": "https://chatgpt.com/c/456"},
            {"type": "page", "url": "https://mail.google.com/mail/u/0/"},
            {"type": "other", "url": "https://example.com"}
        ]
        mock_response.read.return_value = json.dumps(mock_tabs).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = agy_cli.check_opera_neon_health()

        self.assertEqual(result["status"], "ONLINE")
        self.assertEqual(result["tab_count"], 3)
        self.assertTrue(result["has_claude"])
        self.assertTrue(result["has_chatgpt"])
        self.assertTrue(result["has_gmail"])

    @patch("agy_cli.urllib.request.urlopen")
    def test_check_opera_neon_health_no_ai_tabs(self, mock_urlopen):
        mock_response = MagicMock()
        mock_tabs = [
            {"type": "page", "url": "https://example.com"},
        ]
        mock_response.read.return_value = json.dumps(mock_tabs).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = agy_cli.check_opera_neon_health()

        self.assertEqual(result["status"], "ONLINE")
        self.assertEqual(result["tab_count"], 1)
        self.assertFalse(result["has_claude"])
        self.assertFalse(result["has_chatgpt"])
        self.assertFalse(result["has_gmail"])


    @patch("agy_cli.urllib.request.urlopen")
    def test_check_opera_neon_health_failure(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection timeout")

        result = agy_cli.check_opera_neon_health()

        self.assertEqual(result["status"], "OFFLINE")
        self.assertEqual(result["error"], "Connection timeout")

if __name__ == "__main__":
    unittest.main()
