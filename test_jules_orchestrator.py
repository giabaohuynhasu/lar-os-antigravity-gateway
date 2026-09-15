import unittest
from unittest.mock import patch
import json
import os
from pathlib import Path

from jules_orchestrator import JulesOrchestrator, KEYS_FILE

class TestJulesOrchestrator(unittest.TestCase):
    @patch.dict(os.environ, clear=True) # Ensure JULES_API_KEY is not set
    @patch('pathlib.Path.read_text')
    @patch('builtins.print')
    def test_load_keys_error_handling(self, mock_print, mock_read_text):
        """Test _load_keys handles read_text exception gracefully."""
        # Set up the mock to raise a json.JSONDecodeError
        mock_read_text.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)

        # In __init__, it calls _load_keys which checks self.keys_file.exists().
        # Since we want it to enter the block and hit read_text, we mock exists to return True.
        with patch('pathlib.Path.exists', return_value=True):
            # Also patch the fallback file path to not exist, so it returns [] instead of raising an error
            # trying to parse a non-existent fallback or passing
            with patch('pathlib.Path.is_file', return_value=False):
                orchestrator = JulesOrchestrator()

                # Assertions
                mock_read_text.assert_called_once_with(encoding='utf-8')
                mock_print.assert_called_once()
                self.assertTrue(mock_print.call_args[0][0].startswith("[JulesOrchestrator] Failed to load keys:"))

                # Assert that keys is an empty list
                self.assertEqual(orchestrator.keys, [])

if __name__ == '__main__':
    unittest.main()
