import unittest
from unittest.mock import patch, MagicMock
from cloud_shell_bridge import run_remote_command, run_remote_python, NODES

class TestCloudShellBridge(unittest.TestCase):
    @patch('cloud_shell_bridge.subprocess.run')
    def test_run_remote_command_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "hello"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        ret = run_remote_command("echo hello")
        if isinstance(ret, dict):
            code = ret.get("returncode")
            out = ret.get("stdout")
            err = ret.get("stderr")
        else:
            code, out, err = ret

        self.assertEqual(code, 0)
        self.assertEqual(out, "hello")
        self.assertEqual(err, "")
        mock_run.assert_called_once()

    @patch('cloud_shell_bridge.subprocess.run')
    def test_run_remote_command_invalid_node(self, mock_run):
        with self.assertRaises(ValueError):
            run_remote_command("echo hello", node_name="invalid_node")

    @patch('cloud_shell_bridge.subprocess.run')
    def test_run_remote_python_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "world"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        ret = run_remote_python("print('world')")
        if isinstance(ret, dict):
            code = ret.get("returncode")
            out = ret.get("stdout")
            err = ret.get("stderr")
        else:
            code, out, err = ret

        self.assertEqual(code, 0)
        self.assertEqual(out, "world")
        self.assertEqual(err, "")
        mock_run.assert_called_once()

    @patch('cloud_shell_bridge.subprocess.run')
    def test_run_remote_python_invalid_node(self, mock_run):
        with self.assertRaises(ValueError):
            run_remote_python("print('world')", node_name="invalid_node")

if __name__ == '__main__':
    unittest.main()
