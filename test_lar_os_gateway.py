import unittest
import random
from unittest.mock import patch
import lar_os_gateway

class TestLarOsGateway(unittest.TestCase):

    def test_decorrelated_jitter_standard(self):
        with patch('random.uniform') as mock_uniform:
            mock_uniform.return_value = 0.27
            result = lar_os_gateway.decorrelated_jitter(0.1)
            self.assertEqual(result, 0.27)
            mock_uniform.assert_called_once()
            args, _ = mock_uniform.call_args
            self.assertEqual(args[0], 0.25)
            self.assertAlmostEqual(args[1], 0.3)

    def test_decorrelated_jitter_cap(self):
        with patch('random.uniform') as mock_uniform:
            mock_uniform.return_value = 2.5
            result = lar_os_gateway.decorrelated_jitter(1.0)
            self.assertEqual(result, 2.0)
            mock_uniform.assert_called_with(0.25, 3.0)

    def test_decorrelated_jitter_custom_params(self):
        with patch('random.uniform') as mock_uniform:
            mock_uniform.return_value = 4.5
            result = lar_os_gateway.decorrelated_jitter(2.0, base=1.0, cap=5.0)
            self.assertEqual(result, 4.5)
            mock_uniform.assert_called_with(1.0, 6.0)

    def test_decorrelated_jitter_zero_previous(self):
        with patch('random.uniform') as mock_uniform:
            mock_uniform.return_value = 0.25
            result = lar_os_gateway.decorrelated_jitter(0.0)
            self.assertEqual(result, 0.25)
            args, _ = mock_uniform.call_args
            if args[1] == 0.0:
                mock_uniform.assert_called_with(0.25, 0.0)
            else:
                mock_uniform.assert_called_with(0.25, 0.25)

if __name__ == '__main__':
    unittest.main()
