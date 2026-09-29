import unittest
from unittest.mock import patch
import os

from vibe_interpreter import interpret_vibe, VibeResult

class TestVibeInterpreter(unittest.TestCase):
    def test_no_args_interactive(self):
        res = interpret_vibe([])
        self.assertEqual(res.action, "interactive")
        self.assertEqual(res.prompt, "")

    def test_status_flags(self):
        res = interpret_vibe(["-s"])
        self.assertEqual(res.action, "status")

        res = interpret_vibe(["--status"])
        self.assertEqual(res.action, "status")

    def test_inbox_flags(self):
        res = interpret_vibe(["-i"])
        self.assertEqual(res.action, "inbox")

        res = interpret_vibe(["--inbox"])
        self.assertEqual(res.action, "inbox")

    def test_interactive_no_prompt(self):
        res = interpret_vibe(["-m", "gpt"])
        self.assertEqual(res.action, "interactive")
        self.assertEqual(res.model, "gpt")

    def test_status_vibe(self):
        for tc in ["st", "status", "check he thong", "khoe ko"]:
            res = interpret_vibe(tc.split())
            self.assertEqual(res.action, "status", f"Failed for {tc}")

    def test_inbox_vibe(self):
        for tc in ["ib", "inbox", "hop thu"]:
            res = interpret_vibe(tc.split())
            self.assertEqual(res.action, "inbox", f"Failed for {tc}")

    def test_interactive_vibe(self):
        for tc in ["chat", "talk", "tro chuyen", "interactive"]:
            res = interpret_vibe(tc.split())
            self.assertEqual(res.action, "interactive", f"Failed for {tc}")

    def test_model_routing_claude(self):
        res = interpret_vibe(["claude", "viet", "ham", "kiem", "tra"])
        self.assertEqual(res.action, "query")
        self.assertEqual(res.model, "claude")
        self.assertEqual(res.prompt, "viet ham kiem tra")

    def test_model_routing_gpt(self):
        res = interpret_vibe(["gpt", "giai", "thich", "code"])
        self.assertEqual(res.action, "query")
        self.assertEqual(res.model, "chatgpt")
        self.assertEqual(res.prompt, "giai thich code")

    def test_model_routing_pro(self):
        res = interpret_vibe(["pro", "phan", "tich", "data"])
        self.assertEqual(res.action, "query")
        self.assertEqual(res.model, "gemini-3.5-pro")
        self.assertEqual(res.prompt, "phan tich data")

    def test_model_routing_default_flash(self):
        res = interpret_vibe(["giai", "thich", "ve", "antigravity"])
        self.assertEqual(res.action, "query")
        self.assertEqual(res.model, "gemini-3.5-flash")
        self.assertEqual(res.prompt, "giai thich ve antigravity")

    @patch.dict(os.environ, {"AGY_AUTO_EMAIL": "0"}, clear=True)
    def test_email_intent(self):
        res = interpret_vibe(["gui", "mail", "bao", "cao"])
        self.assertEqual(res.action, "query")
        self.assertTrue(res.send_email)
        self.assertEqual(res.prompt, "bao cao")

        res = interpret_vibe(["tom", "tat", "roi", "gui", "mail", "cho", "tui"])
        self.assertEqual(res.action, "query")
        self.assertTrue(res.send_email)
        self.assertEqual(res.prompt, "tom tat")

        res = interpret_vibe(["viet", "regex", "email"])
        self.assertEqual(res.action, "query")
        self.assertFalse(res.send_email)
        self.assertEqual(res.prompt, "viet regex email")

    @patch.dict(os.environ, {"AGY_AUTO_EMAIL": "1"}, clear=True)
    def test_auto_email_env(self):
        res = interpret_vibe(["giai", "thich", "code"])
        self.assertEqual(res.action, "query")
        self.assertTrue(res.send_email)

if __name__ == "__main__":
    unittest.main()
