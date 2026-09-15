"""
Unit Tests for Perplexity Comet Infinite Substrate Bridge
Author: Gia Bao Huynh (Jun) / LAR-OS
"""

import unittest
from unittest.mock import patch
from comet_perplexity_bridge import is_comet_cdp_alive, get_perplexity_tab, COMET_CDP_PORT

class TestCometPerplexityBridge(unittest.TestCase):

    def test_comet_cdp_daemon_is_listening(self):
        """Verify that Comet CDP daemon is live on port 9225"""
        self.assertTrue(is_comet_cdp_alive(), f"Comet CDP daemon must be listening on port {COMET_CDP_PORT}")

    def test_get_perplexity_tab(self):
        """Verify that Perplexity tab is discovered in Comet browser"""
        tab = get_perplexity_tab()
        self.assertIsNotNone(tab, "Should locate an open tab in Comet browser")
        self.assertIn("webSocketDebuggerUrl", tab, "Tab must expose webSocketDebuggerUrl")
        self.assertIn("id", tab)

    def test_perplexity_tab_domain(self):
        """Verify that Perplexity domain is present in active tab metadata"""
        tab = get_perplexity_tab()
        self.assertIsNotNone(tab)
        url = tab.get("url", "")
        self.assertTrue(
            "perplexity.ai" in url or "chrome://" in url,
            f"Expected tab URL to be valid, got: {url}"
        )

    @patch("builtins.print")
    @patch("urllib.request.urlopen")
    def test_get_perplexity_tab_error(self, mock_urlopen, mock_print):
        """Verify that get_perplexity_tab handles errors properly"""
        mock_urlopen.side_effect = Exception("Mocked connection error")
        tab = get_perplexity_tab()
        self.assertIsNone(tab)
        mock_print.assert_called_once()

if __name__ == "__main__":
    unittest.main()
