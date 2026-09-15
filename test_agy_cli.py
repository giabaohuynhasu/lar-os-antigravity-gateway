import unittest
from unittest.mock import patch
import urllib.error

from agy_cli import check_gateway_health

class TestAgyCli(unittest.TestCase):
    @patch('urllib.request.urlopen')
    def test_check_gateway_health_error(self, mock_urlopen):
        # Setup the mock to raise an exception
        mock_urlopen.side_effect = urllib.error.URLError('Connection refused')

        # Call the function
        result = check_gateway_health()

        # Assert the expected result format for errors
        self.assertEqual(result, {"status": "error", "message": "<urlopen error Connection refused>"})

if __name__ == '__main__':
    unittest.main()
