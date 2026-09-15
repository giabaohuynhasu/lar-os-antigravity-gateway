import unittest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path
from jules_orchestrator import JulesOrchestrator

class TestJulesOrchestrator(unittest.TestCase):

    @patch("jules_orchestrator.os.environ.get")
    @patch("jules_orchestrator.Path.read_text")
    @patch("builtins.print")
    def test_load_keys_json_decode_error(self, mock_print, mock_read_text, mock_env_get):
        # Ensure we don't return an env key
        mock_env_get.return_value = None
        # Simulate a JSONDecodeError when reading the keys file
        mock_read_text.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)

        orchestrator = JulesOrchestrator()

        # It should return an empty list when an error occurs
        self.assertEqual(orchestrator.keys, [])

        # Verify print was called with the correct error message format
        mock_print.assert_called_once()
        print_call_args = mock_print.call_args[0][0]
        self.assertTrue(print_call_args.startswith("[JulesOrchestrator] Failed to load keys:"))

    @patch("jules_orchestrator.os.environ.get")
    @patch("jules_orchestrator.Path.read_text")
    @patch("builtins.print")
    def test_load_keys_io_error(self, mock_print, mock_read_text, mock_env_get):
        # Ensure we don't return an env key
        mock_env_get.return_value = None
        # Simulate an IOError when reading the keys file
        mock_read_text.side_effect = IOError("File not found")

        orchestrator = JulesOrchestrator()

        # It should return an empty list when an error occurs
        self.assertEqual(orchestrator.keys, [])

        # Verify print was called
        mock_print.assert_called_once()
        print_call_args = mock_print.call_args[0][0]
        self.assertTrue(print_call_args.startswith("[JulesOrchestrator] Failed to load keys:"))

if __name__ == "__main__":
    unittest.main()
