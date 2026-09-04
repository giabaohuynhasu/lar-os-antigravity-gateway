"""
Unit Tests for Gemini Spark <-> Antigravity Communication Hub & Gmail Dispatcher
Author: Gia Bao Huynh (Jun) / Antigravity
"""

import unittest
import asyncio
import json
import time
from pathlib import Path
import tempfile
import sys

GATEWAY_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(GATEWAY_DIR))

from gemini_spark_bridge import GeminiSparkBridge
from gmail_spark_sender import GmailSparkSender
from gemini_spark_daemon import GeminiSparkDaemon

class TestGeminiSparkBridge(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.bridge = GeminiSparkBridge(bridge_dir=self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_structure(self):
        self.assertTrue(self.bridge.inbox_file.exists())
        self.assertTrue(self.bridge.status_file.exists())
        self.assertTrue(self.bridge.reports_dir.exists())
        self.assertTrue(self.bridge.archive_dir.exists())

        status = self.bridge.get_status()
        self.assertEqual(status.get("state"), "IDLE")

    def test_read_and_consume_command(self):
        # Empty inbox should return None
        self.assertIsNone(self.bridge.read_pending_command())

        # Write test command
        prompt_text = "Phân tích trạng thái kết nối của hệ thống Antigravity và báo cáo qua Gmail"
        self.bridge.inbox_file.write_text(f"# Header\n\n{prompt_text}\n", encoding="utf-8")

        cmd = self.bridge.read_pending_command()
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd["prompt"], prompt_text)
        self.assertTrue(cmd["id"].startswith("cmd_"))

        # Consume command
        self.bridge.consume_command(cmd["id"], cmd["prompt"])
        self.assertIsNone(self.bridge.read_pending_command())

        # Verify archive
        archives = list(self.bridge.archive_dir.glob("*.md"))
        self.assertEqual(len(archives), 1)
        self.assertIn(prompt_text, archives[0].read_text(encoding="utf-8"))

    def test_save_report(self):
        title = "Báo Cáo Thử Nghiệm"
        md = "# Báo cáo thử nghiệm\n\nNội dung chi tiết."
        html = "<h1>Báo cáo thử nghiệm</h1>"
        saved_path = self.bridge.save_report(title, md, html)
        self.assertTrue(saved_path.exists())
        self.assertIn("Báo_Cáo_Thử_Nghiệm", saved_path.name)

class TestGmailSparkSender(unittest.TestCase):
    def setUp(self):
        self.sender = GmailSparkSender(port=9224)

    def test_gmail_tab_discovery(self):
        tab = self.sender.get_or_open_gmail_tab()
        self.assertIsNotNone(tab, "Gmail tab should be detected on Opera Neon CDP")
        self.assertIn("mail.google.com", tab.get("url", ""))

class TestGeminiSparkDaemon(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.daemon = GeminiSparkDaemon(check_interval_seconds=1)
        self.daemon.bridge = GeminiSparkBridge(bridge_dir=self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_format_html_report(self):
        html = self.daemon.format_html_report("Test Subject", "Test Prompt", "Test Response Body")
        self.assertIn("Antigravity x Gemini Spark Report", html)
        self.assertIn("thuaquan228@gmail.com", html)
        self.assertIn("Test Prompt", html)
        self.assertIn("Test Response Body", html)

if __name__ == "__main__":
    unittest.main()
