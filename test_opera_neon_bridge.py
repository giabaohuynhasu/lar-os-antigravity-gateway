"""
Unit Tests for Opera Neon AI Bridge & Gateway Integration
Author: Gia Bao Huynh (Jun) / Antigravity
"""

import unittest
import asyncio
import json
import sys
from pathlib import Path

# Ensure paths
GATEWAY_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GATEWAY_DIR))

from opera_neon_ai_bridge import OperaNeonBridge, AI_TARGETS, consult_opera_neon
from lar_os_gateway import MCP_TOOLS_DEFINITIONS, handle_mcp_jsonrpc

class TestOperaNeonBridge(unittest.TestCase):
    def setUp(self):
        self.bridge = OperaNeonBridge(port=9224)

    def test_targets_configuration(self):
        self.assertIn("chatgpt", AI_TARGETS)
        self.assertIn("deepseek", AI_TARGETS)
        self.assertIn("kimi", AI_TARGETS)
        for engine, cfg in AI_TARGETS.items():
            self.assertIn("name", cfg)
            self.assertIn("url", cfg)
            self.assertIn("input_selector", cfg)
            self.assertIn("send_selector", cfg)
            self.assertIn("response_selector", cfg)

    def test_bridge_is_alive(self):
        alive = self.bridge.is_alive()
        self.assertTrue(alive, "Opera Neon must be alive on CDP port 9224")

    def test_list_tabs(self):
        tabs = self.bridge.list_tabs()
        self.assertIsInstance(tabs, list)
        self.assertGreater(len(tabs), 0, "Opera Neon should have at least 1 tab open")
        titles = [t.get("title", "") for t in tabs]
        self.assertTrue(any("chatgpt" in t.get("url", "").lower() for t in tabs), "ChatGPT tab should exist in Opera Neon")

    def test_inspect_kimi_status(self):
        status = asyncio.run(self.bridge.inspect_target_status("kimi"))
        self.assertIsInstance(status, dict)
        self.assertEqual(status.get("engine"), "kimi")
        self.assertIn("title", status)
        self.assertIn("has_cloudflare_turnstile", status)

    def test_mcp_tool_definition(self):
        tool_names = [t["name"] for t in MCP_TOOLS_DEFINITIONS]
        self.assertIn("opera_neon_consult", tool_names)
        neon_tool = next(t for t in MCP_TOOLS_DEFINITIONS if t["name"] == "opera_neon_consult")
        props = neon_tool["inputSchema"]["properties"]
        self.assertIn("engine", props)
        self.assertIn("prompt", props)
        self.assertEqual(props["engine"]["enum"], ["chatgpt", "deepseek", "kimi"])

    def test_mcp_jsonrpc_tools_list(self):
        req = {"id": "test-1", "method": "tools/list", "params": {}}
        res = asyncio.run(handle_mcp_jsonrpc(req))
        tools = res.get("result", {}).get("tools", [])
        tool_names = [t["name"] for t in tools]
        self.assertIn("opera_neon_consult", tool_names)

    def test_offline_bridge_fallback(self):
        offline_bridge = OperaNeonBridge(port=19999)
        self.assertFalse(offline_bridge.is_alive())
        tabs = offline_bridge.list_tabs()
        self.assertEqual(tabs, [])

if __name__ == "__main__":
    unittest.main()
