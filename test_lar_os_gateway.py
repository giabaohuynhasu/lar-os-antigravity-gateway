import unittest
from unittest.mock import patch, MagicMock
import socket
from pathlib import Path
from lar_os_gateway import CLIProxyWatchdog

class TestCLIProxyWatchdog(unittest.TestCase):
    def setUp(self):
        self.watchdog = CLIProxyWatchdog(Path("dummy.exe"), Path("dummy.json"))
        self.watchdog.port = 18798

    @patch('socket.socket')
    def test_check_tcp_port_success(self, mock_socket_class):
        mock_socket_instance = MagicMock()
        mock_context = MagicMock()

        # When socket.socket() is called, it returns mock_socket_instance
        mock_socket_class.return_value = mock_socket_instance

        # When the context manager __enter__ is called on mock_socket_instance,
        # it returns mock_context (which represents `s` inside the `with` block)
        mock_socket_instance.__enter__.return_value = mock_context

        self.assertTrue(self.watchdog.check_tcp_port())

        mock_socket_class.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_context.settimeout.assert_called_once_with(0.5)
        mock_context.connect.assert_called_once_with(("127.0.0.1", 18798))

    @patch('socket.socket')
    def test_check_tcp_port_failure_connection_refused(self, mock_socket_class):
        mock_socket_instance = MagicMock()
        mock_context = MagicMock()

        mock_socket_class.return_value = mock_socket_instance
        mock_socket_instance.__enter__.return_value = mock_context

        mock_context.connect.side_effect = ConnectionRefusedError("Connection refused")

        self.assertFalse(self.watchdog.check_tcp_port())

        mock_context.connect.assert_called_once_with(("127.0.0.1", 18798))

    @patch('socket.socket')
    def test_check_tcp_port_failure_timeout(self, mock_socket_class):
        mock_socket_instance = MagicMock()
        mock_context = MagicMock()

        mock_socket_class.return_value = mock_socket_instance
        mock_socket_instance.__enter__.return_value = mock_context

        mock_context.connect.side_effect = socket.timeout("timed out")

        self.assertFalse(self.watchdog.check_tcp_port())

        mock_context.connect.assert_called_once_with(("127.0.0.1", 18798))

if __name__ == '__main__':
    unittest.main()
