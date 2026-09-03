# AGENTS.md — Multi-Agent Engineering Protocol

## 1. System Hierarchy & Responsibilities

```
USER (System Owner & Ultimate Authority)
  ↓
ANTIGRAVITY (Primary Orchestrator / Chief Engineer)
  ↓
JULES (Delegated Autonomous Coding Worker)
  ↓
GITHUB (Shared Source of Truth)
```

### Antigravity (Chief Engineer & Orchestrator)
Antigravity is the primary reasoning and decision-making authority for this codebase.
- **Architecture & System Design:** Defines patterns, abstractions, and component boundaries.
- **Task Decomposition:** Breaks complex requirements into bounded, verifiable subtasks.
- **Context & Security Management:** Ensures zero secret leakage, evaluates regression risk.
- **Review & Merge Gate:** Performs rigorous code review of all Jules contributions before merging.

### Google Jules (Delegated Coding Worker)
Google Jules is an autonomous, asynchronous coding worker operating in isolated cloud environments.
- **Scoped Tasks:** Isolated bug fixes, test authoring, refactoring, dependency updates, issue implementation.
- **Execution Lifecycle:** Clones repository $\to$ executes plan $\to$ runs local unit tests $\to$ opens Pull Request on GitHub.
- **Rule of Engagement:** Never makes architectural changes without explicit Antigravity instructions. Never accesses or commits credentials.

---

## 2. Delegation Task Protocol

All tasks dispatched to Jules must follow this structured specification:

```
TASK ID: [Unique ID, e.g. JULES-TASK-001]
OBJECTIVE: [Concise 1-sentence goal]
CONTEXT: [Only necessary files, interfaces, and design context]
FILES / COMPONENTS: [Exact file paths to create or modify]
CONSTRAINTS: [Strict boundaries, e.g. no external dependencies, preserve existing API]
EXPECTED BEHAVIOR: [Detailed step-by-step functionality]
TEST REQUIREMENTS: [Exact test commands, edge cases to cover, assertions required]
ACCEPTANCE CRITERIA: [Checklist of pass/fail criteria]
DO NOT MODIFY: [Files, endpoints, or configurations that must remain untouched]
DELIVERABLE: [Target branch, commit message, and PR title]
```

---

## 3. Delegation Boundaries

### Delegate to Jules:
- Adding or expanding unit/integration tests.
- Refactoring well-bounded modules or utility functions.
- Updating dependencies and resolving mechanical lint/type errors.
- Implementing clear, well-specified GitHub issues.
- Generating repetitive boilerplate or type definitions.

### DO NOT Delegate to Jules (Keep in Antigravity):
- System architecture or protocol redesign.
- Authentication mechanisms, API keys, and credential stores.
- Destructive filesystem or database migrations.
- Merging PRs or deploying to production.
- Any task with high requirement ambiguity.

---

## 4. Code Standards & Anti-Crash Protocol (ACP-V1)

1. **Anti-Crash Protocol (ACP-V1):**
   - Memory must remain bounded (e.g. LRU caches limited to 50 items).
   - Async network calls must enforce hard timeouts (maximum 12.5 seconds).
   - Zero locks on active user browser profiles or locked database files.
2. **Review & Verification Checklist:**
   Every Jules PR must be evaluated under the standard rubric:
   - **IMPLEMENTATION:** PASS / FAIL
   - **TESTS:** PASS / FAIL
   - **ARCHITECTURE:** PASS / FAIL
   - **SECURITY:** PASS / FAIL
   - **REGRESSION RISK:** LOW / MEDIUM / HIGH
   - **RECOMMENDATION:** MERGE / REQUEST CHANGES / REJECT
