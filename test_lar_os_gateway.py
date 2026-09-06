import unittest
from lar_os_gateway import get_provider_code, PROVIDER_CODE_MAP

class TestGetProviderCode(unittest.TestCase):
    def test_valid_provider(self):
        if "giabaohuynh0512@gmail.com" in PROVIDER_CODE_MAP:
            self.assertEqual(get_provider_code("giabaohuynh0512@gmail.com"), PROVIDER_CODE_MAP["giabaohuynh0512@gmail.com"])
        if "ENV_DEFAULT" in PROVIDER_CODE_MAP:
            self.assertEqual(get_provider_code("ENV_DEFAULT"), PROVIDER_CODE_MAP["ENV_DEFAULT"])
        if "none" in PROVIDER_CODE_MAP:
            self.assertEqual(get_provider_code("none"), PROVIDER_CODE_MAP["none"])

    def test_unknown_provider(self):
        unknown_str = "unknown_provider"
        # Should be calculated using hash and modulo
        expected_val = 10 + (abs(hash(unknown_str)) % 90)
        self.assertEqual(get_provider_code(unknown_str), expected_val)

    def test_empty_string(self):
        self.assertEqual(get_provider_code(""), 0)
        self.assertEqual(get_provider_code("   "), 0)

    def test_none_value(self):
        self.assertEqual(get_provider_code(None), 0)

    def test_unexpected_types(self):
        self.assertEqual(get_provider_code(123), 0)
        self.assertEqual(get_provider_code(3.14), 0)
        self.assertEqual(get_provider_code(["a", "b"]), 0)
        self.assertEqual(get_provider_code({"a": 1}), 0)

if __name__ == '__main__':
    unittest.main()
