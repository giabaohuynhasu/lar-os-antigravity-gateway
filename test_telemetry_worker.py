import unittest
from unittest.mock import MagicMock
from pathlib import Path
from lar_os_gateway import TelemetryWorker

class TestTelemetryWorkerStop(unittest.TestCase):
    def test_stop(self):
        # Initialize the worker
        worker = TelemetryWorker(Path("dummy.db"))

        # Set up internal state
        worker._running = True

        # Mock _queue and _worker_thread
        mock_queue = MagicMock()
        mock_thread = MagicMock()

        worker._queue = mock_queue
        worker._worker_thread = mock_thread

        # Call the method under test
        worker.stop()

        # Assertions
        # 1. _running is False
        self.assertFalse(worker._running)

        # 2. None is put in _queue
        mock_queue.put.assert_called_once_with(None)

        # 3. _worker_thread joins
        mock_thread.join.assert_called_once_with(timeout=2.0)

if __name__ == '__main__':
    unittest.main()
