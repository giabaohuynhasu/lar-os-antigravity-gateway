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

### Google Jules (Autonomous AI Co-Engineer & Senior Developer)
Google Jules is an autonomous, asynchronous coding agent operating with expanded developer authority across isolated environments and cloud services:
- **Expanded Scoped Tasks:** Architectural module authoring, complex refactoring, test suite development, feature implementation, and cross-file integration.
- **Google AI Studio Integration:**
  - Full access to Google AI Studio API via `google_ai_studio_client.py` (models: `gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-2.5-pro`).
  - Authorized to execute LLM extraction pipelines (`SPEC.md` Section 2), synthetic test fixtures, anti-sycophancy audits, and code verification loops.
- **Execution Lifecycle:** Clones repository $\to$ executes plan $\to$ calls AI Studio when needed $\to$ runs local unit tests $\to$ outputs clean git patches and Pull Requests.
- **Security Invariant:** Anti-Crash Protocol (ACP-V1) applies strictly. Zero credential leakage to git history or logs.

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
AI STUDIO CAPABILITIES: [Enabled Gemini models, extraction tasks, synthetic data generation]
TEST REQUIREMENTS: [Exact test commands, edge cases to cover, assertions required]
ACCEPTANCE CRITERIA: [Checklist of pass/fail criteria]
DO NOT MODIFY: [Files, endpoints, or configurations that must remain untouched]
DELIVERABLE: [Target branch, commit message, and PR title]
```

---

## 3. Delegation Boundaries & Elevated Authority

### Full Authority Granted to Jules:
- End-to-end module authoring and expanding test suites (`test_*.py`).
- Calling Google AI Studio for automated text analysis, LLM extraction (`extract_research_object`), and evaluation.
- Refactoring complex multi-file structures with backward compatibility.
- Executing isolated test loops and performance benchmarks.
- Implementing feature requests from GitHub issues and specifications.

### Kept in Antigravity (Chief Orchestrator Oversight):
- Master security policy enforcement and final PR merge decisions.
- Multi-account rotation pool management.
- Multi-platform synchronization (GitHub, Hugging Face, Google Drive, Obsidian, Zenodo).
- High-level architectural strategy and system governance.

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

---

## 5. Mandatory ChatGPT Consultation Protocol (User Directive)

**LỆNH BẮT BUỘC: LUÔN THAM VẤN CHATGPT CHO MỌI TASK**

Mọi tác vụ kỹ thuật, kiến trúc, coding, refactoring, debug và tối ưu hóa hệ thống đều phải tuân thủ nghiêm ngặt quy trình tham vấn ChatGPT:
1. **Tham vấn đầu tiên:** Antigravity/Jules phải kết nối với ChatGPT qua Opera Neon CDP (cổng 9224) để lấy tư vấn phương án kỹ thuật và code mẫu trước khi triển khai.
2. **Ràng buộc vàng:** Mọi giải pháp từ ChatGPT phải tuân thủ điều kiện **"KHÔNG ĐƯỢC NẶNG MÁY"** (RAM < 45MB, CPU idle ~0%, zero Docker/Redis/Prometheus/Grafana).
3. **Thẩm định & Đối chiếu:** Đưa ý kiến của ChatGPT vào bản thiết kế/implementation plan và nghiệm thu kết quả sau khi hoàn thành.
