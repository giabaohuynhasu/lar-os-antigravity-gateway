import unittest
from unittest.mock import patch
import sys
import io
from nlm_safe import run_nlm

class TestNlmSafe(unittest.TestCase):
    @patch('nlm_safe.ensure_authenticated')
    def test_run_nlm_empty_args(self, mock_ensure_auth):
        """Test run_nlm when args is empty. Should print usage and return."""
        mock_ensure_auth.return_value = True # Ensure auth doesn't fail

        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            run_nlm([])
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__

        self.assertEqual(captured_output.getvalue().strip(), "Sử dụng: nlm_safe.py <lệnh>")
        mock_ensure_auth.assert_called_once()

    @patch('nlm_safe.ensure_authenticated')
    @patch('nlm_safe.subprocess.run')
    def test_run_nlm_with_args(self, mock_subproc_run, mock_ensure_auth):
        """Test run_nlm when args are provided. Should run command and exit."""
        mock_ensure_auth.return_value = True

        # Mock subprocess.run to return a successful run with returncode 0
        mock_subproc_run.return_value.returncode = 0

        with self.assertRaises(SystemExit) as cm:
            run_nlm(["test", "arg"])

        self.assertEqual(cm.exception.code, 0)
        mock_ensure_auth.assert_called_once()
        mock_subproc_run.assert_called_once()

    @patch('nlm_safe.ensure_authenticated')
    @patch('nlm_safe.subprocess.run')
    def test_run_nlm_with_args_fail(self, mock_subproc_run, mock_ensure_auth):
        """Test run_nlm when args are provided and subprocess fails."""
        mock_ensure_auth.return_value = True

        # Mock subprocess.run to return a failed run with returncode 1
        mock_subproc_run.return_value.returncode = 1

        with self.assertRaises(SystemExit) as cm:
            run_nlm(["test", "arg"])

        self.assertEqual(cm.exception.code, 1)
        mock_ensure_auth.assert_called_once()
        mock_subproc_run.assert_called_once()

if __name__ == '__main__':
    unittest.main()
