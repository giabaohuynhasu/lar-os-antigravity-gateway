import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import sys
import os

from agy_cli import (
    check_gateway_health,
    check_opera_neon_health,
    query_model,
    has_stdin_data,
    GATEWAY_URL
)

class TestAgyCli(unittest.IsolatedAsyncioTestCase):

    @patch('urllib.request.urlopen')
    def test_check_gateway_health_online(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"status": "ONLINE", "mode": "5-Pro Pool"}).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = check_gateway_health()

        self.assertEqual(result.get("status"), "ONLINE")
        self.assertEqual(result.get("mode"), "5-Pro Pool")
        mock_urlopen.assert_called_once()

    @patch('urllib.request.urlopen')
    def test_check_gateway_health_offline(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused")

        result = check_gateway_health()

        self.assertEqual(result.get("status"), "OFFLINE")
        self.assertIn("Connection refused", result.get("error"))

    @patch('urllib.request.urlopen')
    def test_check_opera_neon_health_online(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_tabs = [
            {"type": "page", "url": "https://claude.ai/chat"},
            {"type": "page", "url": "https://chatgpt.com/"},
            {"type": "page", "url": "https://mail.google.com/"},
            {"type": "background_page", "url": "chrome-extension://..."}
        ]
        mock_resp.read.return_value = json.dumps(mock_tabs).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = check_opera_neon_health()

        self.assertEqual(result.get("status"), "ONLINE")
        self.assertEqual(result.get("tab_count"), 3)
        self.assertTrue(result.get("has_claude"))
        self.assertTrue(result.get("has_chatgpt"))
        self.assertTrue(result.get("has_gmail"))

    @patch('urllib.request.urlopen')
    def test_check_opera_neon_health_offline(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused")

        result = check_opera_neon_health()

        self.assertEqual(result.get("status"), "OFFLINE")

    @patch('opera_neon_ai_bridge.consult_opera_neon')
    async def test_query_model_claude(self, mock_consult):
        mock_consult.return_value = {"response": "Claude response"}

        result = await query_model("Hello", model="claude")

        self.assertEqual(result, "Claude response")
        mock_consult.assert_called_once_with(engine="claude", prompt="Hello")

    @patch('urllib.request.urlopen')
    async def test_query_model_gateway_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_gateway_response = {
            "choices": [{"message": {"content": "Gateway response"}}]
        }
        mock_resp.read.return_value = json.dumps(mock_gateway_response).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = await query_model("Hello", model="gemini-3.5-flash")

        self.assertEqual(result, "Gateway response")

    @patch('urllib.request.urlopen')
    async def test_query_model_gateway_error(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused")

        result = await query_model("Hello", model="gemini-3.5-flash")

        self.assertIn("Error", result)
        self.assertIn("Connection refused", result)

    @patch('sys.stdin')
    def test_has_stdin_data(self, mock_stdin):
        # We just test the simple path
        mock_stdin.isatty.return_value = True
        self.assertFalse(has_stdin_data())

    @patch('sys.stdin')
    @patch('sys.platform', 'win32')
    @patch.dict('sys.modules', {'msvcrt': MagicMock(), 'ctypes': MagicMock()})
    def test_has_stdin_data_win32_mock(self, mock_stdin):
        # We test the cross-platform import mock as instructed by AGENTS.md
        mock_stdin.isatty.return_value = False
        # If it doesn't fail with ModuleNotFoundError, the test is successful
        try:
            has_stdin_data()
        except ModuleNotFoundError:
            self.fail("has_stdin_data() raised ModuleNotFoundError on win32 branch")

if __name__ == '__main__':
    unittest.main()
