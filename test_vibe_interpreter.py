import unittest
from vibe_interpreter import strip_accents

class TestVibeInterpreter(unittest.TestCase):

    def test_strip_accents_basic(self):
        """Test with basic unaccented strings."""
        self.assertEqual(strip_accents("hello"), "hello")
        self.assertEqual(strip_accents("world"), "world")
        self.assertEqual(strip_accents("python test"), "python test")

    def test_strip_accents_vietnamese(self):
        """Test with common Vietnamese diacritics and special characters."""
        self.assertEqual(strip_accents("đường"), "duong")
        self.assertEqual(strip_accents("tiếng việt"), "tieng viet")
        self.assertEqual(strip_accents("Nguyễn Văn A"), "nguyen van a")
        self.assertEqual(strip_accents("Xin chào thế giới"), "xin chao the gioi")

    def test_strip_accents_uppercase(self):
        """Test uppercase letters with accents."""
        self.assertEqual(strip_accents("ĐẠI HỌC"), "dai hoc")
        self.assertEqual(strip_accents("HÀ NỘI"), "ha noi")
        self.assertEqual(strip_accents("VIỆT NAM"), "viet nam")

    def test_strip_accents_empty(self):
        """Test empty string."""
        self.assertEqual(strip_accents(""), "")

    def test_strip_accents_mixed(self):
        """Test mixed accented, unaccented, and special characters."""
        self.assertEqual(strip_accents("Cảm ơn! 123 @#$"), "cam on! 123 @#$")
        self.assertEqual(strip_accents("Đăng ký (Sign up)"), "dang ky (sign up)")

if __name__ == "__main__":
    unittest.main()
