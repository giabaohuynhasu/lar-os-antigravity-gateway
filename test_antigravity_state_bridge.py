import unittest
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

if __name__ == "__main__":
    unittest.main()
