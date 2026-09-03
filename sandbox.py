"""
sandbox.py -- Third-Order Audit reference implementation & enhanced epistemic engine.

Structural checker for a research corpus, following Huynh (2026), "The
Third-Order Audit" and "The Research Sandbox". Answers three narrow,
answerable questions about a set of research objects (papers/claims):

  Order 1 -- does a stated, specific falsification condition exist?
  Order 2 -- does at least one falsification condition point OUTWARD,
             at something checkable independent of the corpus's own
             vocabulary (a dated event, an independent paper, a primary
             source), rather than only at internal terms?
  Order 3 -- across the whole loaded set, do revision events over time
             narrow/withdraw claims more often than they merely
             reaffirm them unchanged after a challenge (Lakatos
             progressive vs. degenerating, operationalized as a
             category count rather than a fabricated numeric metric)?

WHAT THIS TOOL DOES NOT DO (read this before trusting any output number):
  - It does not verify truth. It checks STRUCTURE: does an exit
    condition exist, does it point outward, does the revision record
    show real movement. A paper can pass every check here and still be
    wrong about the world.
  - It does not verify its own input. Whether
    `references_external_source=True` is an honest coding decision, or
    a coder (human or AI) writing what makes the paper pass, is exactly
    the kind of thing Goodhart's Law (Strathern, 1997) warns a measure
    stops being able to detect once it becomes a target. Every
    ResearchObject loaded into this tool should carry a `source_note`
    on each FalsificationCondition and Revision stating WHO coded it
    and WHAT they checked it against, so a second party can contest a
    specific coding decision rather than the tool's output as a whole.
  - `third_break_boundary_risk` flags an object whose own audit asks an
    evaluating agent (human or AI) to assess something about ITS OWN
    state, sincerity, or bias -- the condition under which a stateless
    AI collaborator's usual "no accumulated commitment" protection does
    not apply (Huynh 2026, "The Third Break"). A flagged object is not
    wrong; it just needs a different kind of check than this tool runs.

ENHANCEMENTS (SPEC.md Section 3 & 4 compliant):
  - Confidence labeling (HIGH, MEDIUM, LOW, UNVERIFIED) per condition & revision.
  - AuditLog and human override tracking (preserves immutable original coder history).
  - Dual-pass inter-coder consensus measurement via diff_report().
  - Backward compatible with example_corpus.json and CLI commands (load, diff, new).

USAGE
    python3 sandbox.py load corpus_data.json          # full report
    python3 sandbox.py diff original.json recoded.json # compare two codings
    python3 sandbox.py new                             # print an empty template
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional
import json
import sys
import datetime


class DeltaType(Enum):
    """What kind of change a single revision event actually was.
    Deliberately categorical, not a fabricated numeric distance between
    claim-states -- see The Research Sandbox, Section I, on why a
    formal state-transition notation was rejected as a "formalization
    illusion" that adds no empirical constraint."""
    NARROWED = "narrowed"       # claim's scope was reduced in response to a challenge
    WITHDRAWN = "withdrawn"     # claim was retracted outright
    REAFFIRMED = "reaffirmed"   # claim was restated unchanged after a substantive challenge
    EXTENDED = "extended"       # new material was added; not a revision of a prior claim


class ConfidenceLevel(Enum):
    """Confidence label for evidence mapping (SPEC.md Section 3).
    Prevents hiding uncertain LLM guesses behind clean booleans."""
    HIGH = "HIGH"               # Direct quotation/DOI/verifiable primary record verified
    MEDIUM = "MEDIUM"           # Secondary reference or plausible external trace
    LOW = "LOW"                 # Inferred from context with limited provenance
    UNVERIFIED = "UNVERIFIED"   # Source paywalled, inaccessible, or ambiguous


@dataclass
class FalsificationCondition:
    """One stated exit condition for a claim."""
    id: str
    text: str = ""
    references_external_source: bool = False
    # WHO coded this flag and WHAT they checked it against. Leaving this
    # blank is allowed but defeats the tool's main safeguard -- see the
    # module docstring's Goodhart's Law warning.
    source_note: str = ""
    confidence: str = ConfidenceLevel.HIGH.value
    external_anchor: str = ""  # URL, DOI, or cited external passage (SPEC.md Sec 3)


@dataclass
class Revision:
    """One documented event in which a claim actually changed (or was
    challenged and did not change)."""
    delta_type: DeltaType
    trigger: str            # what prompted the revision -- a dated event, a critique, a check
    note: str = ""
    source_note: str = ""   # who documented this event and against what record
    confidence: str = ConfidenceLevel.HIGH.value
    external_anchor: str = ""


@dataclass
class AuditLogEntry:
    """Tracks human review or model recoding overrides (SPEC.md Section 3)."""
    timestamp: str
    reviewer: str
    field_changed: str
    old_value: Any
    new_value: Any
    rationale: str


@dataclass
class ResearchObject:
    """A single paper/claim under audit."""
    id: str
    title: str = ""
    falsification_conditions: List[FalsificationCondition] = field(default_factory=list)
    revisions: List[Revision] = field(default_factory=list)
    self_referential_audit_present: bool = False
    audit_history: List[AuditLogEntry] = field(default_factory=list)

    def order1_pass(self) -> bool:
        """Order 1: at least one stated, specific falsification condition exists."""
        return len(self.falsification_conditions) > 0

    def order2_pass(self) -> bool:
        """Order 2: at least one falsification condition is checkable against
        something outside the corpus's own vocabulary (a dated event, an
        independent paper, a primary source) rather than only internal terms."""
        return any(fc.references_external_source for fc in self.falsification_conditions)

    def third_break_boundary_risk(self) -> bool:
        """Flags an object whose audit process asks the evaluating agent to
        assess something about ITS OWN state, sincerity, or bias -- the exact
        condition under which The Third Break shows statelessness protections
        do not apply."""
        return self.self_referential_audit_present

    def apply_override(self, reviewer: str, field_name: str, new_value: Any, rationale: str) -> None:
        """Applies a human override with mandatory audit logging (SPEC.md Section 3 & 4)."""
        old_val = getattr(self, field_name, None)
        setattr(self, field_name, new_value)
        entry = AuditLogEntry(
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            reviewer=reviewer,
            field_changed=field_name,
            old_value=str(old_val),
            new_value=str(new_value),
            rationale=rationale
        )
        self.audit_history.append(entry)

    def flags(self) -> List[str]:
        out = []
        if not self.order1_pass():
            out.append("NO_FALSIFICATION_CONDITION")
        if not self.order2_pass():
            out.append("NO_EXTERNAL_CHECKABLE_CONDITION")
        if self.third_break_boundary_risk():
            out.append("THIRD_BREAK_BOUNDARY_RISK")
        return out

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        for rev in d["revisions"]:
            rev["delta_type"] = rev["delta_type"].value if isinstance(rev["delta_type"], DeltaType) else rev["delta_type"]
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ResearchObject":
        fcs = []
        for fc in d.get("falsification_conditions", []):
            fc_dict = dict(fc)
            if "confidence" not in fc_dict:
                fc_dict["confidence"] = ConfidenceLevel.HIGH.value
            if "external_anchor" not in fc_dict:
                fc_dict["external_anchor"] = ""
            fcs.append(FalsificationCondition(**fc_dict))

        revs = []
        for r in d.get("revisions", []):
            r_dict = dict(r)
            r_dict["delta_type"] = DeltaType(r_dict["delta_type"]) if not isinstance(r_dict["delta_type"], DeltaType) else r_dict["delta_type"]
            if "confidence" not in r_dict:
                r_dict["confidence"] = ConfidenceLevel.HIGH.value
            if "external_anchor" not in r_dict:
                r_dict["external_anchor"] = ""
            revs.append(Revision(**r_dict))

        history = []
        for h in d.get("audit_history", []):
            history.append(AuditLogEntry(**h))

        return ResearchObject(
            id=d["id"],
            title=d.get("title", ""),
            falsification_conditions=fcs,
            revisions=revs,
            self_referential_audit_present=d.get("self_referential_audit_present", False),
            audit_history=history
        )


@dataclass
class ResearchSandbox:
    """Holds a loaded set of ResearchObjects and runs the programme-level
    (Order 3) check across all of them."""
    objects: List[ResearchObject] = field(default_factory=list)

    def order3_programme_report(self) -> Dict[str, Any]:
        """Lakatos check, computed honestly: not a fake numerical distance
        between claim-states, but a simple, auditable count of how many
        real revision events narrowed/withdrew a claim versus merely
        reaffirmed it unchanged after challenge."""
        total = narrowed_or_withdrawn = reaffirmed = extended = 0
        reaffirmed_cases = []
        for obj in self.objects:
            for rev in obj.revisions:
                total += 1
                if rev.delta_type in (DeltaType.NARROWED, DeltaType.WITHDRAWN):
                    narrowed_or_withdrawn += 1
                elif rev.delta_type == DeltaType.REAFFIRMED:
                    reaffirmed += 1
                    reaffirmed_cases.append({"paper": obj.id, "trigger": rev.trigger})
                elif rev.delta_type == DeltaType.EXTENDED:
                    extended += 1
        return {
            "total_revision_events": total,
            "narrowed_or_withdrawn": narrowed_or_withdrawn,
            "reaffirmed_unchanged": reaffirmed,
            "extended_new_material": extended,
            "constraint_ratio": round(narrowed_or_withdrawn / total, 3) if total else None,
            "reaffirmed_unchanged_cases": reaffirmed_cases,
        }

    def flagged_papers_report(self) -> Dict[str, List[str]]:
        out = {}
        for obj in self.objects:
            f = obj.flags()
            if f:
                out[obj.id] = f
        return out

    def full_report(self) -> Dict[str, Any]:
        return {
            "programme_level": self.order3_programme_report(),
            "flagged_papers": self.flagged_papers_report(),
            "n_objects": len(self.objects),
            "n_passing_both_orders": sum(
                1 for o in self.objects if o.order1_pass() and o.order2_pass()
            ),
        }

    def to_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"objects": [o.to_dict() for o in self.objects]}, f, indent=2)

    @staticmethod
    def from_json(path: str) -> "ResearchSandbox":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ResearchSandbox(objects=[ResearchObject.from_dict(o) for o in data["objects"]])


def diff_report(a: ResearchObject, b: ResearchObject) -> Dict[str, Any]:
    """Compare two independent codings of the SAME research object (e.g.
    an original coding vs. an independent recoding by a different party)
    and report exactly what differs, rather than silently overwriting one
    with the other. This is the tool's main defense against the Goodhart's
    Law risk named in the module docstring: a disagreement here is a
    signal to look at the underlying claim again, not noise to average away.
    """
    if a.id != b.id:
        raise ValueError(f"diff_report compares two codings of the SAME object; got '{a.id}' vs '{b.id}'")

    a_triggers = {(r.delta_type, r.trigger) for r in a.revisions}
    b_triggers = {(r.delta_type, r.trigger) for r in b.revisions}

    return {
        "id": a.id,
        "order1_pass_agree": a.order1_pass() == b.order1_pass(),
        "order2_pass_agree": a.order2_pass() == b.order2_pass(),
        "a_order1_order2": (a.order1_pass(), a.order2_pass()),
        "b_order1_order2": (b.order1_pass(), b.order2_pass()),
        "revisions_only_in_a": [{"delta_type": d.value, "trigger": t} for d, t in (a_triggers - b_triggers)],
        "revisions_only_in_b": [{"delta_type": d.value, "trigger": t} for d, t in (b_triggers - a_triggers)],
        "revisions_in_both": [{"delta_type": d.value, "trigger": t} for d, t in (a_triggers & b_triggers)],
        "agrees_exactly": a_triggers == b_triggers and a.order1_pass() == b.order1_pass() and a.order2_pass() == b.order2_pass(),
    }


def empty_template() -> Dict[str, Any]:
    """A blank ResearchObject shape, for hand-coding a new paper or for an
    LLM extraction prompt to target as its output schema."""
    return {
        "objects": [
            {
                "id": "example_paper_id",
                "title": "Example Paper Title",
                "falsification_conditions": [
                    {
                        "id": "F-Example1",
                        "text": "State the exact condition here.",
                        "references_external_source": True,
                        "source_note": "Who coded this and what they checked it against.",
                        "confidence": "HIGH",
                        "external_anchor": "DOI or URL or verifiable quote"
                    }
                ],
                "revisions": [
                    {
                        "delta_type": "narrowed",
                        "trigger": "What prompted this revision.",
                        "note": "",
                        "source_note": "Who documented this and against what record.",
                        "confidence": "HIGH",
                        "external_anchor": "Dated event or publication"
                    }
                ],
                "self_referential_audit_present": False,
                "audit_history": []
            }
        ]
    }


def _cli():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "load" and len(sys.argv) == 3:
        sb = ResearchSandbox.from_json(sys.argv[2])
        print(json.dumps(sb.full_report(), indent=2))
    elif cmd == "diff" and len(sys.argv) == 4:
        sb_a = ResearchSandbox.from_json(sys.argv[2])
        sb_b = ResearchSandbox.from_json(sys.argv[3])
        by_id_b = {o.id: o for o in sb_b.objects}
        for obj_a in sb_a.objects:
            if obj_a.id in by_id_b:
                print(json.dumps(diff_report(obj_a, by_id_b[obj_a.id]), indent=2))
    elif cmd == "new":
        print(json.dumps(empty_template(), indent=2))
    else:
        print(__doc__)


if __name__ == "__main__":
    _cli()
