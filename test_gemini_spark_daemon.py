import unittest
import os
from unittest.mock import patch, MagicMock
from gemini_spark_daemon import GeminiSparkDaemon

# Ensure required environment variables for testing modules if any (e.g. for antigravity_state_bridge)
os.environ["LAR_OS_AHCP_SHARED_SECRET"] = "dummy_secret"

class TestGeminiSparkDaemon(unittest.IsolatedAsyncioTestCase):

    @patch('urllib.request.urlopen')
    @patch('builtins.print')
    async def test_call_gateway_ai_error(self, mock_print, mock_urlopen):
        """Tests that a network error in call_gateway_ai correctly returns the fallback error string."""

        # Setup the exception to be raised when urlopen is called
        mock_urlopen.side_effect = Exception("Connection refused")

        # Initialize daemon (mock check interval so it starts fast)
        daemon = GeminiSparkDaemon(check_interval_seconds=1)

        # Call the method
        prompt = "Test prompt"
        result = await daemon.call_gateway_ai(prompt)

        # Verify the returned string matches expected fallback format
        self.assertEqual(result, "[Error] Gateway call failed: Connection refused")

        # Verify that print was called with correct fallback message format
        mock_print.assert_called_with("[Daemon] Failed to call gateway AI: Connection refused")

if __name__ == '__main__':
    unittest.main()
