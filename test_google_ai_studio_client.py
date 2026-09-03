import unittest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path
from google_ai_studio_client import GoogleAIStudioClient

class TestGoogleAIStudioClient(unittest.TestCase):
    def setUp(self):
        self.client = GoogleAIStudioClient()

    def test_client_initialization(self):
        self.assertEqual(self.client.model, "gemini-3.6-flash")
        self.assertTrue(len(self.client.keys) > 0)

    def test_get_active_key_rotates(self):
        k1 = self.client.get_active_key()
        k2 = self.client.get_active_key()
        self.assertTrue(len(k1) > 0)
        self.assertTrue(len(k2) > 0)

    @patch("urllib.request.urlopen")
    def test_generate_content_mock(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "candidates": [{
                "content": {
                    "parts": [{"text": "Synthetic response from Gemini 3.6 Flash"}]
                }
            }]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.generate_content("Ping test")
        self.assertEqual(res["text"], "Synthetic response from Gemini 3.6 Flash")
        self.assertEqual(res["model"], "gemini-3.6-flash")

    @patch("urllib.request.urlopen")
    def test_extract_research_object_mock(self, mock_urlopen):
        sample_json = {
            "id": "paper_test",
            "title": "A Mock Paper",
            "falsification_conditions": [{
                "id": "F-1",
                "text": "Condition 1",
                "references_external_source": True,
                "source_note": "Verified by test",
                "confidence": "HIGH",
                "external_anchor": "10.5281/zenodo.12345"
            }],
            "revisions": [{
                "delta_type": "narrowed",
                "trigger": "Refined hypothesis",
                "note": "",
                "source_note": "Checked record",
                "confidence": "HIGH",
                "external_anchor": "Event 2026"
            }],
            "self_referential_audit_present": False
        }
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "candidates": [{
                "content": {
                    "parts": [{"text": json.dumps(sample_json)}]
                }
            }]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        ro = self.client.extract_research_object("Mock text", "paper_test")
        self.assertEqual(ro["id"], "paper_test")
        self.assertTrue(ro["falsification_conditions"][0]["references_external_source"])
        self.assertEqual(ro["revisions"][0]["delta_type"], "narrowed")

if __name__ == "__main__":
    unittest.main()
