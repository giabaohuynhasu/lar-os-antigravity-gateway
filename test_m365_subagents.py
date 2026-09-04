import unittest
import sys
import os
from pathlib import Path

from m365_subagents import M365_SUBAGENTS, list_subagents

class TestM365Subagents(unittest.TestCase):
    def test_registry_has_core_agents(self):
        expected_keys = [
            "bio_audit",
            "epistemic_3rd",
            "synthesis_core",
            "devops_sentinel",
            "institutional_strategist"
        ]
        agents = list_subagents()
        agent_ids = [a["id"] for a in agents]
        for ek in expected_keys:
            self.assertIn(ek, agent_ids)
            self.assertIn(ek, M365_SUBAGENTS)

    def test_agent_directives_contain_mandatory_sections(self):
        for aid, ainfo in M365_SUBAGENTS.items():
            self.assertTrue(len(ainfo["name"]) > 5)
            self.assertTrue(len(ainfo["role"]) > 5)
            self.assertTrue(len(ainfo["description"]) > 10)
            self.assertIn("RULES:", ainfo["directive"])
            self.assertIn("OUTPUT STRUCTURE:", ainfo["directive"])

    def test_bio_audit_falsification_invariant(self):
        bio_agent = M365_SUBAGENTS["bio_audit"]
        self.assertIn("Falsification", bio_agent["directive"])
        self.assertIn("stratification", bio_agent["directive"].lower())

    def test_epistemic_3rd_order_invariants(self):
        epistemic = M365_SUBAGENTS["epistemic_3rd"]
        self.assertIn("Order 1", epistemic["directive"])
        self.assertIn("Order 2", epistemic["directive"])
        self.assertIn("Order 3", epistemic["directive"])
        self.assertIn("Goodhart", epistemic["directive"])

if __name__ == "__main__":
    unittest.main()
