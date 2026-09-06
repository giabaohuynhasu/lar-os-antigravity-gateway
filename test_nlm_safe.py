import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import nlm_safe

class TestNlmSafe(unittest.TestCase):

    @patch.dict(os.environ, {}, clear=True)
    @patch('builtins.print')
    def test_ensure_authenticated_missing_api_key(self, mock_print):
        with self.assertRaises(SystemExit) as cm:
            nlm_safe.ensure_authenticated()
        self.assertEqual(cm.exception.code, 1)
        mock_print.assert_called_with("[!] Không tìm thấy GEMINI_API_KEY. Vui lòng thiết lập biến môi trường này.")

if __name__ == '__main__':
    unittest.main()
