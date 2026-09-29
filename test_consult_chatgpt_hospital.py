import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import sys
import io

# Import main after setting up imports correctly
import consult_chatgpt_hospital

class TestConsultChatGPTHospital(unittest.IsolatedAsyncioTestCase):
    @patch('consult_chatgpt_hospital.aiohttp.ClientSession')
    @patch('consult_chatgpt_hospital.websockets.connect')
    async def test_main_with_mocked_aiohttp(self, mock_ws_connect, mock_session_class):
        # Setup mocked session
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        # Mock activation response
        mock_activate_resp = AsyncMock()
        mock_activate_resp.text.return_value = "Activated"
        mock_activate_ctx = AsyncMock()
        mock_activate_ctx.__aenter__.return_value = mock_activate_resp

        # Mock json response
        mock_json_resp = AsyncMock()
        mock_json_resp.json.return_value = [
            {"id": consult_chatgpt_hospital.TARGET_ID, "webSocketDebuggerUrl": "ws://mock-url"}
        ]
        mock_json_ctx = AsyncMock()
        mock_json_ctx.__aenter__.return_value = mock_json_resp

        # Configure session.get
        # We need to return a MagicMock that returns an async context manager,
        # because the side_effect logic for an AsyncMock doesn't handle sync
        # return types (like the async context manager) properly if they are awaited.
        def side_effect(url, *args, **kwargs):
            if "/activate/" in url:
                return mock_activate_ctx
            elif url.endswith("/json"):
                return mock_json_ctx
            raise ValueError(f"Unexpected url {url}")

        mock_session.get = MagicMock(side_effect=side_effect)

        # Setup mocked websocket
        mock_ws = AsyncMock()
        mock_ws_connect.return_value.__aenter__.return_value = mock_ws

        # Mock websocket recv to simulate a response
        # 1. baseline count
        # 2. inject prompt
        # 3. response streaming

        # We just need to make the script exit quickly. We can do that by making ws.recv timeout immediately
        # except when we provide specific responses.

        # For simplicity, let's just make it raise an exception or mock sys.exit to stop the test
        # Actually, let's just let it run. But we need to speed up the asyncio.sleep.

        # Wait, the best way to test the aiohttp part is to mock ws to just throw an exception to exit early
        # Since we just want to verify the HTTP part
        mock_ws.send.side_effect = Exception("Stop test after HTTP calls")

        # Redirect stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            await consult_chatgpt_hospital.main()
        except Exception as e:
            if str(e) != "Stop test after HTTP calls":
                raise
        finally:
            sys.stdout = sys.__stdout__

        output = captured_output.getvalue()

        # Verify
        self.assertIn("[1] Activating Opera Neon tab...", output)
        self.assertIn("  -> Tab activation: Activated", output)
        self.assertIn("[2] Connected to WebSocket debugger", output)

        # Verify aiohttp was called correctly
        mock_session.get.assert_any_call(f"http://127.0.0.1:9224/json/activate/{consult_chatgpt_hospital.TARGET_ID}")
        mock_session.get.assert_any_call("http://127.0.0.1:9224/json")

if __name__ == '__main__':
    unittest.main()
