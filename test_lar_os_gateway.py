import unittest
from unittest.mock import patch, mock_open
import json

from lar_os_gateway import get_config

class TestLarOsGateway(unittest.TestCase):
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_config_exception(self, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_file.side_effect = PermissionError("Permission denied")

        config = get_config()

        self.assertEqual(config, {
            "gateway": {"port": 18797, "host": "127.0.0.1", "auth_token": "lar-os-master"}
        })
        mock_file.assert_called_once()

if __name__ == '__main__':
    unittest.main()
