import unittest
from unittest.mock import patch, MagicMock
import sys
import subprocess

from nlm_safe import ensure_authenticated, run_nlm, NLM_PATH

class TestNlmSafe(unittest.TestCase):

    @patch('nlm_safe.subprocess.run')
    def test_ensure_authenticated_success(self, mock_run):
        # Mock successful initial check
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = ensure_authenticated()

        self.assertTrue(result)
        mock_run.assert_called_once_with(
            [str(NLM_PATH), "login", "--check"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

    @patch('nlm_safe.subprocess.run')
    def test_ensure_authenticated_reauth_success(self, mock_run):
        # Mock failed check, then successful login
        mock_check = MagicMock()
        mock_check.returncode = 1

        mock_login = MagicMock()
        mock_login.returncode = 0

        mock_run.side_effect = [mock_check, mock_login]

        result = ensure_authenticated()

        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)

        mock_run.assert_any_call(
            [str(NLM_PATH), "login", "--check"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        mock_run.assert_any_call(
            [str(NLM_PATH), "login"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

    @patch('nlm_safe.subprocess.run')
    def test_ensure_authenticated_reauth_fails(self, mock_run):
        # Mock failed check, then failed login
        mock_check = MagicMock()
        mock_check.returncode = 1

        mock_login = MagicMock()
        mock_login.returncode = 1
        mock_login.stderr = "Login failed error"

        mock_run.side_effect = [mock_check, mock_login]

        result = ensure_authenticated()

        self.assertFalse(result)
        self.assertEqual(mock_run.call_count, 2)

    @patch('nlm_safe.ensure_authenticated')
    @patch('nlm_safe.subprocess.run')
    @patch('nlm_safe.sys.exit')
    def test_run_nlm_authenticated(self, mock_exit, mock_run, mock_ensure):
        # Ensure authenticated returns True
        mock_ensure.return_value = True

        # Mock subprocess run returning 0
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_run.return_value = mock_res

        args = ["arg1", "arg2"]
        run_nlm(args)

        mock_ensure.assert_called_once()
        mock_run.assert_called_once_with([str(NLM_PATH), "arg1", "arg2"])
        mock_exit.assert_called_once_with(0)

    @patch('nlm_safe.ensure_authenticated')
    @patch('nlm_safe.subprocess.run')
    @patch('nlm_safe.sys.exit')
    def test_run_nlm_auth_fails(self, mock_exit, mock_run, mock_ensure):
        # Ensure authenticated returns False
        mock_ensure.return_value = False
        mock_exit.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit) as cm:
            run_nlm(["arg1"])

        self.assertEqual(cm.exception.code, 1)
        mock_ensure.assert_called_once()
        mock_run.assert_not_called()
        mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
