import unittest
from unittest.mock import patch, MagicMock

import sys
import lar_os_gateway

class TestLarOsGateway(unittest.TestCase):
    @patch("builtins.open")
    @patch("sys.__excepthook__") # Mock it just so it doesn't print to console during tests, but don't assert on it
    def test_laros_excepthook_swallows_exception(self, mock_sys_excepthook, mock_open):
        """
        Validates the global exception handler fallback.
        Requires mocking open to raise an OSError (e.g., read-only filesystem)
        and verifying that the internal exception is silently swallowed.
        """
        # Setup mock open to raise an OSError
        mock_open.side_effect = OSError("Read-only file system")

        exc_type = ValueError
        exc_val = ValueError("Test exception")
        exc_tb = MagicMock()

        # Call the excepthook
        try:
            lar_os_gateway._laros_excepthook(exc_type, exc_val, exc_tb)
        except Exception as e:
            self.fail(f"_laros_excepthook raised an exception unexpectedly: {e}")

        self.assertTrue(mock_open.called)

if __name__ == "__main__":
    unittest.main()
