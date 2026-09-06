import unittest
from unittest.mock import patch
import sys
import io
import os

from nlm_safe import ensure_authenticated

class TestNlmSafe(unittest.TestCase):
    @patch('os.environ.get')
    def test_ensure_authenticated_missing_api_key(self, mock_get):
        # Setup mock to return None for any environment variable requested
        mock_get.return_value = None

        # Capture stdout to assert the printed message
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            # We expect a SystemExit(1)
            with self.assertRaises(SystemExit) as cm:
                ensure_authenticated()

            self.assertEqual(cm.exception.code, 1)

            # Verify the error message
            expected_msg = "[!] Không tìm thấy GEMINI_API_KEY. Vui lòng thiết lập biến môi trường này.\n"
            self.assertEqual(captured_output.getvalue(), expected_msg)
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__

if __name__ == '__main__':
    unittest.main()
