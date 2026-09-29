import unittest
from unittest.mock import patch, MagicMock
from cloud_shell_bridge import run_remote_command, run_remote_python, SSH_KEY, NODES

class TestCloudShellBridge(unittest.TestCase):

    @patch("cloud_shell_bridge.subprocess.run")
    def test_run_remote_command_secure_ssh(self, mock_run):
        # Setup mock return value
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Run command
        node_name = "thuaquan228"
        run_remote_command("ls", node_name=node_name)

        # Verify subprocess.run was called
        mock_run.assert_called_once()

        # Get the arguments passed to subprocess.run
        args, kwargs = mock_run.call_args
        ssh_args = args[0]

        # Verify security settings
        self.assertIn("-o", ssh_args)
        self.assertIn("StrictHostKeyChecking=yes", ssh_args)
        self.assertNotIn("StrictHostKeyChecking=no", ssh_args)
        self.assertNotIn("UserKnownHostsFile=/dev/null", ssh_args)

    @patch("cloud_shell_bridge.subprocess.run")
    def test_run_remote_python_secure_ssh(self, mock_run):
        # Setup mock return value
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Run python code
        node_name = "giabaohuynh0512"
        run_remote_python("print('hello')", node_name=node_name)

        # Verify subprocess.run was called
        mock_run.assert_called_once()

        # Get the arguments passed to subprocess.run
        args, kwargs = mock_run.call_args
        ssh_args = args[0]

        # Verify security settings
        self.assertIn("-o", ssh_args)
        self.assertIn("StrictHostKeyChecking=yes", ssh_args)
        self.assertNotIn("StrictHostKeyChecking=no", ssh_args)
        self.assertNotIn("UserKnownHostsFile=/dev/null", ssh_args)

if __name__ == "__main__":
    unittest.main()
