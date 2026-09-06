import unittest
from agy_cli import strip_markdown

class TestAgyCli(unittest.TestCase):
    def test_strip_markdown_bold(self):
        self.assertEqual(strip_markdown("This is **bold** text."), "This is bold text.")
        self.assertEqual(strip_markdown("**bold**"), "bold")

    def test_strip_markdown_italic(self):
        self.assertEqual(strip_markdown("This is _italic_ text."), "This is italic text.")
        self.assertEqual(strip_markdown("_italic_"), "italic")

    def test_strip_markdown_combined(self):
        self.assertEqual(strip_markdown("This is **bold** and _italic_ text."), "This is bold and italic text.")
        self.assertEqual(strip_markdown("**bold**_italic_"), "bolditalic")

    def test_strip_markdown_no_markdown(self):
        self.assertEqual(strip_markdown("Normal text"), "Normal text")

    def test_strip_markdown_empty(self):
        self.assertEqual(strip_markdown(""), "")

    def test_strip_markdown_multiple(self):
        self.assertEqual(strip_markdown("**one** **two** _three_ _four_"), "one two three four")

if __name__ == '__main__':
    unittest.main()
