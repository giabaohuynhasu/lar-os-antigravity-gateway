import unittest
from unittest.mock import patch, MagicMock
import urllib.error
import json

import agy_cli

class TestAgyCli(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_check_gateway_health_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value.decode.return_value = json.dumps({"status": "OK"})
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = agy_cli.check_gateway_health()

        self.assertEqual(result, {"status": "OK"})
        mock_urlopen.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_check_gateway_health_error(self, mock_urlopen):
        # Mock urlopen to raise an exception
        mock_urlopen.side_effect = urllib.error.URLError("Test Error")

        result = agy_cli.check_gateway_health()

        self.assertEqual(result, {"status": "error"})
        mock_urlopen.assert_called_once()

if __name__ == "__main__":
    unittest.main()
