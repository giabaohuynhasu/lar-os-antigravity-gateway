import unittest
from unittest.mock import patch
import os

from vibe_interpreter import interpret_vibe, VibeResult

class TestVibeInterpreter(unittest.TestCase):
    def test_empty_args(self):
        res = interpret_vibe([])
        self.assertEqual(res.action, "interactive")
        self.assertEqual(res.prompt, "")

    def test_standard_flags(self):
        res = interpret_vibe(["-s"])
        self.assertEqual(res.action, "status")

        res = interpret_vibe(["--status"])
        self.assertEqual(res.action, "status")

        res = interpret_vibe(["-i"])
        self.assertEqual(res.action, "inbox")

        res = interpret_vibe(["--inbox"])
        self.assertEqual(res.action, "inbox")

        res = interpret_vibe(["-m", "gpt-4o", "hi"])
        self.assertEqual(res.model, "gpt-4o")

        res = interpret_vibe(["--model=gpt-4o", "hi"])
        self.assertEqual(res.model, "gpt-4o")

        res = interpret_vibe(["-e", "hi"])
        self.assertTrue(res.send_email)

        res = interpret_vibe(["--email", "hi"])
        self.assertTrue(res.send_email)

    def test_status_vibes(self):
        status_cases = [
            ["st"],
            ["status"],
            ["check", "he", "thong"],
            ["khoe", "ko"],
            ["khoe", "khong"],
            ["on", "ko"],
            ["on", "khong"],
            ["song", "ko"],
            ["song", "khong"],
            ["sao", "roi"],
            ["tinh", "hinh"],
            ["ping"],
            ["trang", "thai"]
        ]
        for case in status_cases:
            with self.subTest(case=case):
                res = interpret_vibe(case)
                self.assertEqual(res.action, "status")

    def test_inbox_vibes(self):
        inbox_cases = [
            ["ib"],
            ["inbox"],
            ["hop", "thu"],
            ["hop", "thu", "drive"],
            ["drive", "inbox"],
            ["co", "gi", "moi"],
            ["lenh", "moi"],
            ["pending"],
            ["check", "inbox"]
        ]
        for case in inbox_cases:
            with self.subTest(case=case):
                res = interpret_vibe(case)
                self.assertEqual(res.action, "inbox")

    def test_interactive_vibes(self):
        interactive_cases = [
            ["chat"],
            ["talk"],
            ["tro", "chuyen"],
            ["hoi", "dap"],
            ["tam", "su"],
            ["interactive"]
        ]
        for case in interactive_cases:
            with self.subTest(case=case):
                res = interpret_vibe(case)
                self.assertEqual(res.action, "interactive")
                self.assertEqual(res.prompt, "")

    def test_model_routing(self):
        res = interpret_vibe(["claude", "viet", "ham"])
        self.assertEqual(res.model, "claude")
        self.assertEqual(res.prompt, "viet ham")

        res = interpret_vibe(["sonnet", "hi"])
        self.assertEqual(res.model, "claude")
        self.assertEqual(res.prompt, "hi")

        res = interpret_vibe(["chatgpt", "hi"])
        self.assertEqual(res.model, "chatgpt")
        self.assertEqual(res.prompt, "hi")

        res = interpret_vibe(["gpt", "5", "hi"])
        self.assertEqual(res.model, "chatgpt")
        self.assertEqual(res.prompt, "hi")

        res = interpret_vibe(["pro", "phan", "tich"])
        self.assertEqual(res.model, "gemini-3.5-pro")
        self.assertEqual(res.prompt, "phan tich")

        res = interpret_vibe(["gemini", "pro", "phan", "tich"])
        self.assertEqual(res.model, "gemini-3.5-pro")
        self.assertEqual(res.prompt, "phan tich")

        res = interpret_vibe(["flash", "dich"])
        self.assertEqual(res.model, "gemini-3.5-flash")
        self.assertEqual(res.prompt, "dich")

        res = interpret_vibe(["hoi", "claude", "xem"])
        self.assertEqual(res.model, "claude")

        res = interpret_vibe(["dung", "gpt", "viet"])
        self.assertEqual(res.model, "chatgpt")

        res = interpret_vibe(["can", "pro", "tim"])
        self.assertEqual(res.model, "gemini-3.5-pro")

    def test_email_dispatch(self):
        res = interpret_vibe(["gui", "mail", "bao", "cao"])
        self.assertTrue(res.send_email)
        self.assertEqual(res.prompt, "bao cao")

        res = interpret_vibe(["mail", "bao", "cao"])
        self.assertTrue(res.send_email)
        self.assertEqual(res.prompt, "bao cao")

        res = interpret_vibe(["viet", "bao", "cao", "gui", "gmail", "cho", "tui"])
        self.assertTrue(res.send_email)
        self.assertEqual(res.prompt, "viet bao cao")

        # Technical email prompts should NOT trigger email flag
        res = interpret_vibe(["viet", "regex", "cho", "email"])
        self.assertFalse(res.send_email)

        res = interpret_vibe(["validate", "email", "form"])
        self.assertFalse(res.send_email)

        # Test environment variable fallback
        with patch.dict(os.environ, {"AGY_AUTO_EMAIL": "1"}):
            res = interpret_vibe(["viet", "bao", "cao"])
            self.assertTrue(res.send_email)
            self.assertEqual(res.prompt, "viet bao cao")

        with patch.dict(os.environ, {"AGY_AUTO_EMAIL": "true"}):
            res = interpret_vibe(["viet", "bao", "cao"])
            self.assertTrue(res.send_email)

if __name__ == "__main__":
    unittest.main()
