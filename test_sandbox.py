import unittest
import json
import tempfile
import os
from dataclasses import asdict

from sandbox import (
    ResearchObject,
    FalsificationCondition,
    Revision,
    DeltaType,
    ConfidenceLevel,
    AuditLogEntry,
    ResearchSandbox,
    diff_report,
    empty_template
)

class TestResearchObjectCore(unittest.TestCase):
    def test_order1_pass_true(self):
        obj = ResearchObject(
            id="test1",
            falsification_conditions=[
                FalsificationCondition(id="fc1", text="Test condition")
            ]
        )
        self.assertTrue(obj.order1_pass())

    def test_order1_pass_false(self):
        obj = ResearchObject(id="test1", falsification_conditions=[])
        self.assertFalse(obj.order1_pass())

    def test_order2_pass_true(self):
        obj = ResearchObject(
            id="test1",
            falsification_conditions=[
                FalsificationCondition(id="fc1", references_external_source=False),
                FalsificationCondition(id="fc2", references_external_source=True)
            ]
        )
        self.assertTrue(obj.order2_pass())

    def test_order2_pass_false(self):
        obj = ResearchObject(
            id="test1",
            falsification_conditions=[
                FalsificationCondition(id="fc1", references_external_source=False)
            ]
        )
        self.assertFalse(obj.order2_pass())

    def test_third_break_boundary_risk(self):
        obj = ResearchObject(id="test1", self_referential_audit_present=True)
        self.assertTrue(obj.third_break_boundary_risk())
        
        obj2 = ResearchObject(id="test2", self_referential_audit_present=False)
        self.assertFalse(obj2.third_break_boundary_risk())

    def test_flags(self):
        obj = ResearchObject(id="test1")
        flags = obj.flags()
        self.assertIn("NO_FALSIFICATION_CONDITION", flags)
        self.assertIn("NO_EXTERNAL_CHECKABLE_CONDITION", flags)
        self.assertNotIn("THIRD_BREAK_BOUNDARY_RISK", flags)


class TestResearchObjectEnhancements(unittest.TestCase):
    def test_apply_override_audit_log(self):
        obj = ResearchObject(id="test1", title="Old Title")
        obj.apply_override("reviewer_1", "title", "New Title", "Fixing typo")
        
        self.assertEqual(obj.title, "New Title")
        self.assertEqual(len(obj.audit_history), 1)
        entry = obj.audit_history[0]
        self.assertEqual(entry.reviewer, "reviewer_1")
        self.assertEqual(entry.field_changed, "title")
        self.assertEqual(entry.old_value, "Old Title")
        self.assertEqual(entry.new_value, "New Title")
        self.assertEqual(entry.rationale, "Fixing typo")

    def test_default_confidence_level(self):
        fc = FalsificationCondition(id="fc1")
        self.assertEqual(fc.confidence, ConfidenceLevel.HIGH.value)

        rev = Revision(delta_type=DeltaType.NARROWED, trigger="t")
        self.assertEqual(rev.confidence, ConfidenceLevel.HIGH.value)
        
    def test_from_dict_defaults(self):
        d = {
            "id": "test",
            "falsification_conditions": [{"id": "fc1"}],
            "revisions": [{"delta_type": "narrowed", "trigger": "t"}]
        }
        obj = ResearchObject.from_dict(d)
        self.assertEqual(obj.falsification_conditions[0].confidence, ConfidenceLevel.HIGH.value)
        self.assertEqual(obj.falsification_conditions[0].external_anchor, "")
        self.assertEqual(obj.revisions[0].confidence, ConfidenceLevel.HIGH.value)
        self.assertEqual(obj.revisions[0].external_anchor, "")


class TestResearchSandbox(unittest.TestCase):
    def test_order3_programme_report(self):
        sandbox = ResearchSandbox(objects=[
            ResearchObject(id="test1", revisions=[
                Revision(delta_type=DeltaType.NARROWED, trigger="t1"),
                Revision(delta_type=DeltaType.WITHDRAWN, trigger="t2"),
                Revision(delta_type=DeltaType.REAFFIRMED, trigger="t3"),
                Revision(delta_type=DeltaType.EXTENDED, trigger="t4")
            ])
        ])
        
        report = sandbox.order3_programme_report()
        self.assertEqual(report["total_revision_events"], 4)
        self.assertEqual(report["narrowed_or_withdrawn"], 2)
        self.assertEqual(report["reaffirmed_unchanged"], 1)
        self.assertEqual(report["extended_new_material"], 1)
        self.assertEqual(report["constraint_ratio"], 0.5)
        self.assertEqual(len(report["reaffirmed_unchanged_cases"]), 1)
        self.assertEqual(report["reaffirmed_unchanged_cases"][0], {"paper": "test1", "trigger": "t3"})

    def test_full_report(self):
        sandbox = ResearchSandbox(objects=[
            ResearchObject(id="test1", falsification_conditions=[
                FalsificationCondition(id="fc1", references_external_source=True)
            ])
        ])
        report = sandbox.full_report()
        self.assertEqual(report["n_objects"], 1)
        self.assertEqual(report["n_passing_both_orders"], 1)

    def test_json_serialization(self):
        sandbox = ResearchSandbox(objects=[
            ResearchObject(id="test1", revisions=[
                Revision(delta_type=DeltaType.NARROWED, trigger="t1")
            ])
        ])
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            sandbox.to_json(tmp.name)
            tmp_path = tmp.name

        try:
            loaded_sandbox = ResearchSandbox.from_json(tmp_path)
            self.assertEqual(len(loaded_sandbox.objects), 1)
            self.assertEqual(loaded_sandbox.objects[0].id, "test1")
            self.assertEqual(loaded_sandbox.objects[0].revisions[0].delta_type, DeltaType.NARROWED)
        finally:
            os.remove(tmp_path)


class TestDiffReport(unittest.TestCase):
    def test_diff_report_same(self):
        obj_a = ResearchObject(id="test1", falsification_conditions=[
            FalsificationCondition(id="fc1", references_external_source=True)
        ], revisions=[
            Revision(delta_type=DeltaType.NARROWED, trigger="t1")
        ])
        obj_b = ResearchObject(id="test1", falsification_conditions=[
            FalsificationCondition(id="fc1", references_external_source=True)
        ], revisions=[
            Revision(delta_type=DeltaType.NARROWED, trigger="t1")
        ])
        
        report = diff_report(obj_a, obj_b)
        self.assertTrue(report["agrees_exactly"])
        self.assertTrue(report["order1_pass_agree"])
        self.assertTrue(report["order2_pass_agree"])
        self.assertEqual(len(report["revisions_in_both"]), 1)
        self.assertEqual(len(report["revisions_only_in_a"]), 0)
        self.assertEqual(len(report["revisions_only_in_b"]), 0)

    def test_diff_report_different_revisions(self):
        obj_a = ResearchObject(id="test1", revisions=[
            Revision(delta_type=DeltaType.NARROWED, trigger="t1")
        ])
        obj_b = ResearchObject(id="test1", revisions=[
            Revision(delta_type=DeltaType.WITHDRAWN, trigger="t1")
        ])
        
        report = diff_report(obj_a, obj_b)
        self.assertFalse(report["agrees_exactly"])
        self.assertEqual(len(report["revisions_only_in_a"]), 1)
        self.assertEqual(len(report["revisions_only_in_b"]), 1)

    def test_diff_report_different_id_throws(self):
        obj_a = ResearchObject(id="test1")
        obj_b = ResearchObject(id="test2")
        
        with self.assertRaises(ValueError):
            diff_report(obj_a, obj_b)


class TestExampleCorpus(unittest.TestCase):
    def test_load_example_corpus(self):
        # Assumes example_corpus.json is in the current directory
        # The prompt requires not to delete it, so we can use it directly
        sandbox = ResearchSandbox.from_json("example_corpus.json")
        self.assertEqual(len(sandbox.objects), 2)
        
        obj1 = sandbox.objects[0]
        self.assertEqual(obj1.id, "the_audit_that_missed_itself")
        self.assertTrue(obj1.order1_pass())
        self.assertTrue(obj1.order2_pass())
        
        obj2 = sandbox.objects[1]
        self.assertEqual(obj2.id, "the_load_bearing_test")
        self.assertTrue(obj2.order1_pass())
        self.assertFalse(obj2.order2_pass())
        
        report = sandbox.order3_programme_report()
        self.assertEqual(report["total_revision_events"], 2)
        
        flags = sandbox.flagged_papers_report()
        self.assertIn("the_load_bearing_test", flags)
        self.assertIn("NO_EXTERNAL_CHECKABLE_CONDITION", flags["the_load_bearing_test"])


if __name__ == '__main__':
    unittest.main()
