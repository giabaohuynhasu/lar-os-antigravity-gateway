import unittest
from unittest.mock import patch
import json
import tempfile
from pathlib import Path
from antigravity_state_bridge import compute_signature, create_state_snapshot, verify_handoff_state, HANDOFF_FILE

class TestAntigravityStateBridge(unittest.TestCase):
    def test_compute_signature_deterministic(self):
        d1 = {"a": 1, "b": "test"}
        d2 = {"b": "test", "a": 1}
        self.assertEqual(compute_signature(d1), compute_signature(d2))

    def test_signature_tamper_detection(self):
        d = {"a": 1}
        sig = compute_signature(d)
        d_tampered = {"a": 2}
        self.assertNotEqual(sig, compute_signature(d_tampered))

    def test_create_and_verify_handoff(self):
        package = create_state_snapshot(instance_id="TEST-INSTANCE-01", reason="Unit test execution")
        self.assertIn("header", package)
        self.assertIn("payload", package)
        self.assertEqual(package["payload"]["source_instance"], "TEST-INSTANCE-01")
        self.assertTrue(verify_handoff_state())



    @patch("antigravity_state_bridge.HANDOFF_FILE")
    def test_verify_handoff_state_valid_signature(self, mock_handoff_file):
        mock_handoff_file.exists.return_value = True
        payload = {"a": 1}
        sig = compute_signature(payload)
        mock_handoff_file.read_text.return_value = json.dumps({"header": {"signature": sig}, "payload": payload})
        self.assertTrue(verify_handoff_state())

    @patch("antigravity_state_bridge.HANDOFF_FILE")
    def test_verify_handoff_state_invalid_signature(self, mock_handoff_file):
        mock_handoff_file.exists.return_value = True
        invalid_data = {
            "header": {"signature": "invalid_sig_123"},
            "payload": {"a": 1}
        }
        mock_handoff_file.read_text.return_value = json.dumps(invalid_data)
        self.assertFalse(verify_handoff_state())

    @patch("antigravity_state_bridge.HANDOFF_FILE")
    def test_verify_handoff_state_missing_file(self, mock_handoff_file):
        mock_handoff_file.exists.return_value = False
        self.assertFalse(verify_handoff_state())

if __name__ == "__main__":
    unittest.main()
