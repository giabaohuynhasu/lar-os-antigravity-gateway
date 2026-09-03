"""
Unit Tests for M365 Copilot Infinite Substrate Bridge
Author: Gia Bao Huynh (Jun) / LAR-OS
"""

import unittest
from m365_copilot_bridge import is_cdp_alive, get_copilot_tab, CDP_PORT

class TestM365CopilotBridge(unittest.TestCase):

    def test_cdp_daemon_is_listening(self):
        """Verify that Edge CDP daemon is live on port 9223"""
        self.assertTrue(is_cdp_alive(), f"Edge CDP daemon must be listening on port {CDP_PORT}")

    def test_get_copilot_tab(self):
        """Verify that a valid page tab is discovered on port 9223"""
        tab = get_copilot_tab()
        self.assertIsNotNone(tab, "Should locate an open tab on port 9223")
        self.assertIn("webSocketDebuggerUrl", tab, "Tab must expose webSocketDebuggerUrl")
        self.assertIn("id", tab)

    def test_copilot_tab_url(self):
        """Verify that Copilot domain is present in active tab metadata"""
        tab = get_copilot_tab()
        self.assertIsNotNone(tab)
        url = tab.get("url", "")
        self.assertTrue(
            "copilot" in url or "microsoft" in url or "netflix" in url,
            f"Expected tab URL to be valid, got: {url}"
        )

if __name__ == "__main__":
    unittest.main()
