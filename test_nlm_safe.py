import unittest
from unittest.mock import patch, MagicMock
import sys
import nlm_safe

class TestNlmSafe(unittest.TestCase):
    @patch('subprocess.run')
    def test_ensure_authenticated_success(self, mock_run):
        # Setup
        mock_run.return_value = MagicMock(returncode=0)

        # Execute
        result = nlm_safe.ensure_authenticated()

        # Verify
        self.assertTrue(result)
        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args[0][0][1:], ['login', '--check'])

    @patch('subprocess.run')
    def test_ensure_authenticated_fail_then_success(self, mock_run):
        # Setup
        mock_run.side_effect = [
            MagicMock(returncode=1), # check fails
            MagicMock(returncode=0)  # login succeeds
        ]

        # Execute
        with patch('sys.stderr', new_callable=MagicMock): # Mock stderr to avoid clutter
            result = nlm_safe.ensure_authenticated()

        # Verify
        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)
        self.assertEqual(mock_run.call_args_list[0][0][0][1:], ['login', '--check'])
        self.assertEqual(mock_run.call_args_list[1][0][0][1:], ['login'])

    @patch('subprocess.run')
    def test_ensure_authenticated_fail_then_fail(self, mock_run):
        # Setup
        mock_run.side_effect = [
            MagicMock(returncode=1), # check fails
            MagicMock(returncode=1, stderr="Auth error")  # login fails
        ]

        # Execute
        with patch('sys.stderr', new_callable=MagicMock): # Mock stderr to avoid clutter
            result = nlm_safe.ensure_authenticated()

        # Verify
        self.assertFalse(result)
        self.assertEqual(mock_run.call_count, 2)

    @patch('nlm_safe.ensure_authenticated')
    @patch('subprocess.run')
    @patch('sys.exit')
    def test_run_nlm_auth_success(self, mock_exit, mock_run, mock_ensure_auth):
        # Setup
        mock_ensure_auth.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        mock_exit.side_effect = SystemExit(0)

        # Execute & Verify
        with self.assertRaises(SystemExit) as cm:
            nlm_safe.run_nlm(['some_arg'])

        self.assertEqual(cm.exception.code, 0)
        mock_ensure_auth.assert_called_once()
        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args[0][0][1:], ['some_arg'])

    @patch('nlm_safe.ensure_authenticated')
    @patch('sys.exit')
    def test_run_nlm_auth_fail(self, mock_exit, mock_ensure_auth):
        # Setup
        mock_ensure_auth.return_value = False
        mock_exit.side_effect = SystemExit(1)

        # Execute & Verify
        with self.assertRaises(SystemExit) as cm:
            nlm_safe.run_nlm(['some_arg'])

        self.assertEqual(cm.exception.code, 1)
        mock_ensure_auth.assert_called_once()

    def test_verify_safe_mode(self):
        # Currently it's a pass/no-op, but we ensure it can be called
        # without raising exceptions.
        try:
            nlm_safe.verify_safe_mode()
        except Exception as e:
            self.fail(f"verify_safe_mode raised an exception unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main()