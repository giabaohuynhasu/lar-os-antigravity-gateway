import unittest
import json
import time
from neon_bridge import (
    init_neon_database,
    persist_handoff_to_neon,
    fetch_latest_handoff_from_neon,
    persist_audit_to_neon
)

class TestNeonBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        res = init_neon_database()
        if res.get("status") != "success":
            raise unittest.SkipTest(f"Neon Postgres not available: {res.get('message')}")

    def test_neon_init_tables(self):
        res = init_neon_database()
        self.assertEqual(res.get("status"), "success")

    def test_neon_handoff_persistence_and_retrieval(self):
        test_session_id = f"test-session-{int(time.time())}"
        test_payload = {
            "header": {"protocol": "AHCP-V1", "algorithm": "HMAC-SHA256"},
            "payload": {
                "session_id": test_session_id,
                "timestamp": "2026-09-04T03:00:00Z",
                "state": {"status": "ONLINE", "tests_passed": 36}
            },
            "signature": "test-signature-sha256-hex"
        }
        res = persist_handoff_to_neon(test_payload)
        self.assertEqual(res.get("status"), "success")
        self.assertIsNotNone(res.get("id"))

        latest = fetch_latest_handoff_from_neon()
        self.assertIsNotNone(latest)
        self.assertEqual(latest.get("header", {}).get("protocol"), "AHCP-V1")

    def test_neon_audit_persistence(self):
        test_audit = {
            "hypothesis": "Neon Serverless Postgres provides zero-friction immortal ledgering for LAR-OS.",
            "stated_exit_condition": "Connection loss or cluster downtime",
            "external_anchor": "PostgreSQL 18.6 AWS us-east-2",
            "confidence": "HIGH",
            "source_note": "Integration verification test"
        }
        res = persist_audit_to_neon(test_audit)
        self.assertEqual(res.get("status"), "success")
        self.assertIsNotNone(res.get("id"))

if __name__ == "__main__":
    unittest.main()
