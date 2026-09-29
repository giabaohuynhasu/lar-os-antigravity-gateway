import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import tunnel_bridge

class TestTunnelBridge(unittest.TestCase):

    def test_get_chatgpt_openapi_schema(self):
        test_url = "https://test.trycloudflare.com"
        schema = tunnel_bridge.get_chatgpt_openapi_schema(test_url)

        self.assertIsInstance(schema, dict)
        self.assertEqual(schema["openapi"], "3.1.0")
        self.assertIn("info", schema)
        self.assertIn("servers", schema)
        self.assertIn("paths", schema)

        self.assertEqual(len(schema["servers"]), 1)
        self.assertEqual(schema["servers"][0]["url"], test_url)

        self.assertIn("/v1/chat/completions", schema["paths"])
        self.assertIn("/health", schema["paths"])

    @patch("builtins.open", new_callable=mock_open)
    @patch("tunnel_bridge.DRIVE_DIR")
    @patch("builtins.print")
    def test_generate_chatgpt_openapi_drive_exists(self, mock_print, mock_drive, mock_file):
        mock_drive.exists.return_value = True
        mock_drive.__truediv__.return_value = Path("mocked_drive_path/chatgpt_actions_openapi.json")
        test_url = "https://test.trycloudflare.com"

        tunnel_bridge.generate_chatgpt_openapi(test_url)

        # Open should be called twice (once for local, once for drive)
        self.assertEqual(mock_file.call_count, 2)

        local_path = str(tunnel_bridge.SCRATCH_DIR / "chatgpt_actions_openapi.json")
        drive_path = str(mock_drive / "chatgpt_actions_openapi.json")

        # Get arguments from mock calls
        calls = mock_file.call_args_list
        self.assertEqual(str(calls[0][0][0]), local_path)
        self.assertEqual(str(calls[1][0][0]), drive_path)

        # verify it calls write with a string containing the test URL
        file_handle = mock_file()
        written_content = "".join(call[0][0] for call in file_handle.write.call_args_list)
        self.assertIn(test_url, written_content)

    @patch("builtins.open", new_callable=mock_open)
    @patch("tunnel_bridge.DRIVE_DIR")
    @patch("builtins.print")
    def test_generate_chatgpt_openapi_drive_missing(self, mock_print, mock_drive, mock_file):
        mock_drive.exists.return_value = False
        test_url = "https://test.trycloudflare.com"

        tunnel_bridge.generate_chatgpt_openapi(test_url)

        # Open should be called only once
        self.assertEqual(mock_file.call_count, 1)

        local_path = str(tunnel_bridge.SCRATCH_DIR / "chatgpt_actions_openapi.json")

        # Get arguments from mock calls
        calls = mock_file.call_args_list
        self.assertEqual(str(calls[0][0][0]), local_path)

if __name__ == '__main__':
    unittest.main()
