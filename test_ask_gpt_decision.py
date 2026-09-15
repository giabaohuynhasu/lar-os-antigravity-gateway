import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import json
import ask_gpt_decision

class TestAskGptDecision(unittest.IsolatedAsyncioTestCase):
    @patch('sys.argv', ['ask_gpt_decision.py'])
    @patch('builtins.print')
    @patch('sys.exit')
    async def test_main_no_args(self, mock_exit, mock_print):
        mock_exit.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit) as cm:
            await ask_gpt_decision.main()

        self.assertEqual(cm.exception.code, 1)
        mock_print.assert_called_with("Usage: python ask_gpt_decision.py '<question>'")

    @patch('sys.argv', ['ask_gpt_decision.py', 'test prompt'])
    @patch('builtins.print')
    @patch('ask_gpt_decision.OperaNeonBridge')
    async def test_main_bridge_not_alive(self, mock_bridge_class, mock_print):
        mock_bridge = mock_bridge_class.return_value
        mock_bridge.is_alive.return_value = False

        await ask_gpt_decision.main()

        mock_print.assert_called_with("[-] Opera Neon is not reachable on CDP port 9224")
        mock_bridge.consult_ai.assert_not_called()

    @patch('sys.argv', ['ask_gpt_decision.py', 'What is 2+2?'])
    @patch('builtins.print')
    @patch('ask_gpt_decision.OperaNeonBridge')
    async def test_main_success(self, mock_bridge_class, mock_print):
        mock_bridge = mock_bridge_class.return_value
        mock_bridge.is_alive.return_value = True

        mock_response = {"text": "4"}
        mock_bridge.consult_ai = AsyncMock(return_value=mock_response)

        await ask_gpt_decision.main()

        mock_bridge.consult_ai.assert_called_once_with("chatgpt", "What is 2+2?", timeout_seconds=90)

        # Check that the results were printed correctly
        mock_print.assert_any_call("[*] Sending consultation to ChatGPT in Opera Neon...")
        mock_print.assert_any_call("\n=== KẾT QUẢ TỪ CHATGPT ===")
        mock_print.assert_any_call("4")

    @patch('sys.argv', ['ask_gpt_decision.py', 'What is 2+2?'])
    @patch('builtins.print')
    @patch('ask_gpt_decision.OperaNeonBridge')
    async def test_main_success_no_text_in_response(self, mock_bridge_class, mock_print):
        mock_bridge = mock_bridge_class.return_value
        mock_bridge.is_alive.return_value = True

        mock_response = {"error": "timeout"}
        mock_bridge.consult_ai = AsyncMock(return_value=mock_response)

        await ask_gpt_decision.main()

        mock_bridge.consult_ai.assert_called_once_with("chatgpt", "What is 2+2?", timeout_seconds=90)

        # Check that the fallback json.dumps is used
        mock_print.assert_any_call("[*] Sending consultation to ChatGPT in Opera Neon...")
        mock_print.assert_any_call("\n=== KẾT QUẢ TỪ CHATGPT ===")
        mock_print.assert_any_call(json.dumps(mock_response, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    unittest.main()
