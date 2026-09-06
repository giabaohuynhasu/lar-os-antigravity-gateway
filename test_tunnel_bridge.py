import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import tunnel_bridge

class TestTunnelBridge(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open)
    @patch("tunnel_bridge.Path.exists")
    @patch("builtins.print")
    def test_generate_chatgpt_openapi_servers_url(self, mock_print, mock_exists, mock_file):
        """Test that the OpenAPI schema correctly includes the provided public URL in the servers array."""
        mock_exists.return_value = False

        test_url = "https://example-tunnel.trycloudflare.com"
        tunnel_bridge.generate_chatgpt_openapi(test_url)

        # Verify that open was called to write the file
        mock_file.assert_called_once()

        # Get all arguments passed to write() calls
        write_calls = mock_file().write.call_args_list
        written_content = "".join(call.args[0] for call in write_calls)

        # Parse the JSON string
        schema = json.loads(written_content)

        # Assertions
        self.assertIn("servers", schema)
        self.assertEqual(len(schema["servers"]), 1)
        self.assertEqual(schema["servers"][0]["url"], test_url)

    @patch("builtins.open", new_callable=mock_open)
    @patch("tunnel_bridge.Path.exists")
    @patch("builtins.print")
    def test_generate_chatgpt_openapi_writes_to_drive(self, mock_print, mock_exists, mock_file):
        """Test that the schema is written to Google Drive when the directory exists."""
        mock_exists.return_value = True

        test_url = "https://example-tunnel.trycloudflare.com"
        tunnel_bridge.generate_chatgpt_openapi(test_url)

        # Verify that open was called twice (local and Drive)
        self.assertEqual(mock_file.call_count, 2)

        # Get all arguments passed to write() calls for the Drive file writing
        # Both write operations should have similar content
        self.assertEqual(mock_print.call_count, 2)

if __name__ == '__main__':
    unittest.main()
