# Third-Order Audit — Build Spec

## What this project is

A web tool that takes an uploaded paper (PDF or text) and runs a structural
audit on it: does it state a real falsification condition (Order 1), does
that condition point at something checkable outside the paper's own
vocabulary (Order 2), and — across a whole loaded set of papers — does the
revision history show claims being narrowed/withdrawn under challenge more
than merely reaffirmed unchanged (Order 3, a Lakatos progressive-vs-
degenerating check).

Full theoretical background: Huynh (2026), "The Third-Order Audit" and
"The Research Sandbox." You do not need to read these to build this system;
this spec extracts everything load-bearing.

## What is already built and verified — do not rebuild this

`sandbox.py`, included in this handoff, is a complete, tested reference
implementation of the audit logic:

- `ResearchObject`, `FalsificationCondition`, `Revision`, `DeltaType`,
  `ResearchSandbox` — the full data model.
- `order1_pass()`, `order2_pass()`, `third_break_boundary_risk()` — per-paper
  checks.
- `order3_programme_report()` — the cross-corpus Lakatos ratio.
- `diff_report(a, b)` — compares two independent codings of the *same*
  paper and reports exactly what differs. This is the tool's main defense
  against a coder (human or AI) quietly making the numbers look better; see
  the Goodhart's Law warning in the module docstring before you touch this
  function.
- A JSON schema (`ResearchObject.to_dict` / `from_dict`) and a CLI
  (`python3 sandbox.py load|diff|new`).

Verified end to end: `load`, `diff`, and `new` all run correctly against a
real example dataset (`example_corpus.json`, included). Do not rewrite this
module. Import it. If you need new fields on the data model, extend the
dataclasses — do not fork the logic.

## What needs to be built

### 1. Ingestion
Upload a PDF or paste text. Extract plain text (any standard PDF-to-text
library is fine — this step has no special requirements).

### 2. LLM extraction → schema
Prompt an LLM to read the extracted text and propose a `ResearchObject`
(use `python3 sandbox.py new` for the exact target JSON shape). The prompt
must ask the model to:
- state each falisification condition's exact text as found in the paper
  (not paraphrased away),
- decide `references_external_source` only where it can name *what*
  external thing the condition points at (a date, a paper title, a data
  source) — if it can't name one, the field is `false`,
  and Ask it to justify this decision, don't just return true/false,
- do the same trigger/justification requirement for every `Revision`'s
  `delta_type` classification,
- **always fill in `source_note`** on every condition and revision with a
  one-line justification of the coding decision. This field is not
  optional decoration — it is the only thing that lets a human
  reviewer contest a specific line rather than the whole output.

### 3. The step most likely to be built wrong: evidence mapping

This is not a data-pipeline step. Read this section before implementing it.

A prior test in this same project (see chat history, or ask the person who
commissioned this for the transcript) reconstructed this exact tool from
a paper's own description and ran it against 3 objects the tester had
directly, independently verified. Result: the tester could only confirm
2 of the paper's claimed 11 revision events from primary knowledge — not
because the other 9 were false, but because verifying whether a cited
source actually says what a paper claims requires real judgment
(fetching the source, reading it, deciding if it substantiates the
specific claim), not a lookup.

Consequences for this build:
- Do **not** ship a feature that silently outputs a final `references_
  external_source: true/false` or `delta_type` verdict with no visible
  trail. Every automated coding decision must ship with: (a) the exact
  source it checked (URL, DOI, or quoted passage), (b) a confidence
  label, not a bare boolean, and (c) a one-click way for a human to
  override it, with the override logged rather than silently replacing
  the original.
- Where the extraction pipeline can genuinely run a web search / fetch a
  source and compare it to the claim, do so and show the comparison. Where
  it cannot (paywalled source, ambiguous claim), the UI must say
  "unverified" rather than guessing and hiding the guess behind a clean
  boolean.
- `diff_report()` already exists for exactly this reason: use it to
  surface disagreement between an LLM's first-pass coding and a second,
  independent pass (a second model call with no access to the first
  pass's output, or a human review) rather than presenting only one
  pass's output as final.

### 4. Web UI / API
Standard build. Suggested minimal surface:
- `POST /upload` → returns extracted text + LLM-proposed `ResearchObject` JSON
  (with `source_note`s and confidence labels per field, per Section 3).
- `POST /objects/{id}/review` → human edits/overrides, logged, not silent.
- `GET /corpus/report` → runs `sandbox.py`'s `full_report()` across all
  reviewed (not just proposed) objects.
- `GET /objects/{a}/diff/{b}` → wraps `diff_report()`.
- A results view showing, per paper: Order 1/2 pass-fail with the exact
  condition text and source_note visible on hover/click, and the
  programme-level ratio with every contributing event listed (not just
  the number) — the paper this tool is modeled on treats an unlabeled
  ratio as exactly the kind of "formalization illusion" the whole project
  exists to avoid.

## Files in this handoff
- `sandbox.py` — the verified core module. Import, do not rewrite.
- `example_corpus.json` — working example; running
  `python3 sandbox.py load example_corpus.json` should reproduce the
  output shown in this handoff's accompanying chat message.
