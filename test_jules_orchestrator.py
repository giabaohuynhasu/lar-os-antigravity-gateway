import unittest
import os
import json
from unittest.mock import patch, mock_open, MagicMock, call
from jules_orchestrator import JulesOrchestrator, BASE_URL

class TestJulesOrchestrator(unittest.TestCase):

    @patch.dict(os.environ, {"JULES_API_KEY": "env_test_key"})
    def test_load_keys_env_var(self):
        orchestrator = JulesOrchestrator()
        self.assertEqual(len(orchestrator.keys), 1)
        self.assertEqual(orchestrator.keys[0]["api_key"], "env_test_key")
        self.assertEqual(orchestrator.keys[0]["account"], "env_user")

    @patch.dict(os.environ, {}, clear=True)
    @patch("pathlib.Path.exists")
    def test_load_keys_from_keys_file(self, mock_exists):
        # We want KEYS_FILE.exists() to return True
        def side_effect(*args, **kwargs):
            # Check if this is the KEYS_FILE
            # Note: Path.exists() is called on a Path instance,
            # so self in the mocked method would be the Path object.
            # However, since we mock at class level, it's simpler to just return True.
            pass

        # Since mock_exists replaces Path.exists, let's configure it
        mock_exists.return_value = True

        mocked_data = {
            "jules_keys": [
                {"account": "acc1@test.com", "api_key": "key1", "status": "ACTIVE"},
                {"account": "acc2@test.com", "api_key": "key2", "status": "INACTIVE"}
            ]
        }

        # We need to make sure we only match the open for KEYS_FILE
        # Since _load_keys tries KEYS_FILE first, if it succeeds it returns.
        with patch("builtins.open", mock_open(read_data=json.dumps(mocked_data))):
            orchestrator = JulesOrchestrator()
            self.assertEqual(len(orchestrator.keys), 1)
            self.assertEqual(orchestrator.keys[0]["api_key"], "key1")

    @patch.dict(os.environ, {}, clear=True)
    @patch("pathlib.Path.exists")
    def test_load_keys_fallback_local(self, mock_exists):
        # KEYS_FILE.exists() is False, local_keys.exists() is True
        # The first call is for KEYS_FILE, second is for local_keys
        mock_exists.side_effect = [False, True]

        mocked_data = {
            "jules_keys": [
                {"account": "local@test.com", "api_key": "local_key", "status": "ACTIVE"}
            ]
        }
        with patch("builtins.open", mock_open(read_data=json.dumps(mocked_data))):
            orchestrator = JulesOrchestrator()
            self.assertEqual(len(orchestrator.keys), 1)
            self.assertEqual(orchestrator.keys[0]["api_key"], "local_key")

    @patch.dict(os.environ, {"JULES_API_KEY": "env_test_key"})
    def test_get_api_key_no_keys(self):
        orchestrator = JulesOrchestrator()
        orchestrator.keys = []
        with self.assertRaises(RuntimeError):
            orchestrator.get_api_key()

    @patch.dict(os.environ, {"JULES_API_KEY": "env_test_key"})
    def test_get_api_key_round_robin(self):
        orchestrator = JulesOrchestrator()
        orchestrator.keys = [
            {"account": "a1", "api_key": "k1"},
            {"account": "a2", "api_key": "k2"}
        ]

        k1, a1 = orchestrator.get_api_key()
        self.assertEqual((k1, a1), ("k1", "a1"))

        k2, a2 = orchestrator.get_api_key()
        self.assertEqual((k2, a2), ("k2", "a2"))

        k3, a3 = orchestrator.get_api_key()
        self.assertEqual((k3, a3), ("k1", "a1"))

    @patch.dict(os.environ, {"JULES_API_KEY": "env_test_key"})
    def test_get_api_key_preferred(self):
        orchestrator = JulesOrchestrator()
        orchestrator.keys = [
            {"account": "alpha@test.com", "api_key": "k1"},
            {"account": "beta@test.com", "api_key": "k2"}
        ]

        k, a = orchestrator.get_api_key(preferred_account="beta")
        self.assertEqual((k, a), ("k2", "beta@test.com"))

    @patch("urllib.request.urlopen")
    @patch.dict(os.environ, {"JULES_API_KEY": "test_key"})
    def test_list_sources(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"sources": [{"name": "src1"}]}).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        orchestrator = JulesOrchestrator()
        sources = orchestrator.list_sources()

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["name"], "src1")

        # Verify request details
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, f"{BASE_URL}/sources")
        self.assertEqual(req.method, "GET")
        self.assertEqual(req.headers.get("X-goog-api-key"), "test_key")

    @patch("urllib.request.urlopen")
    @patch.dict(os.environ, {"JULES_API_KEY": "test_key"})
    def test_delegate_to_jules(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"name": "sessions/123"}).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        orchestrator = JulesOrchestrator()
        session = orchestrator.delegate_to_jules(
            task_id="T1",
            objective="obj",
            context="ctx",
            files=["f1"],
            constraints="con",
            expected_behavior="exp",
            test_requirements="test",
            acceptance_criteria="acc",
            do_not_modify="dnm",
            deliverable="del"
        )

        self.assertEqual(session["name"], "sessions/123")
        self.assertEqual(session["_dispatched_by_account"], "env_user")

        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, f"{BASE_URL}/sessions")
        self.assertEqual(req.method, "POST")
        self.assertEqual(req.headers.get("X-goog-api-key"), "test_key")

        payload = json.loads(req.data.decode("utf-8"))
        self.assertTrue("T1" in payload["title"])
        self.assertTrue("obj" in payload["title"])
        self.assertTrue("GOOGLE AI STUDIO ACCESS: [ENABLED]" in payload["prompt"])
        self.assertTrue("f1" in payload["prompt"])

    @patch("urllib.request.urlopen")
    @patch.dict(os.environ, {"JULES_API_KEY": "test_key"})
    def test_check_jules_with_session(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"name": "sessions/456", "state": "DONE"}).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        orchestrator = JulesOrchestrator()
        result = orchestrator.check_jules(session_id="456")

        self.assertEqual(result["state"], "DONE")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, f"{BASE_URL}/sessions/456")
        self.assertEqual(req.method, "GET")

    @patch("urllib.request.urlopen")
    @patch.dict(os.environ, {"JULES_API_KEY": "test_key"})
    def test_check_jules_all(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"sessions": [{"name": "sessions/1"}, {"name": "sessions/2"}]}).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        orchestrator = JulesOrchestrator()
        result = orchestrator.check_jules()

        self.assertEqual(len(result), 2)
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, f"{BASE_URL}/sessions")
        self.assertEqual(req.method, "GET")

    @patch.dict(os.environ, {"JULES_API_KEY": "test_key"})
    def test_review_jules(self):
        orchestrator = JulesOrchestrator()
        summary = {
            "task_id": "T-100",
            "session_id": "S-200",
            "pr_or_branch": "pr-1",
            "implementation": "EXCELLENT",
            "tests": "GOOD",
            "architecture": "PASS",
            "security": "PASS",
            "regression_risk": "NONE",
            "findings": "Looks fine",
            "recommendation": "MERGE IT"
        }
        report = orchestrator.review_jules(summary)

        self.assertIn("T-100", report)
        self.assertIn("S-200", report)
        self.assertIn("EXCELLENT", report)
        self.assertIn("MERGE IT", report)
        self.assertIn("Looks fine", report)

if __name__ == "__main__":
    unittest.main()
