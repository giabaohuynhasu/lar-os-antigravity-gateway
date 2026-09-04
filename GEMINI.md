# GEMINI.md — LAR-OS Project Directives & Behavioral Guardrails

## 1. Cardinal Mandate: Always Consult ChatGPT for Every Task
User (Gia Bao Huynh) has issued a permanent directive:
**LUÔN LUÔN THAM VẤN CHATGPT TRƯỚC CHO MỌI TASK**
- Before implementing code changes, creating complex implementation plans, or making architecture decisions, Antigravity MUST query ChatGPT via the live Opera Neon CDP bridge (port 9224) or discuss the design with GPT.
- Always include the Golden Invariant: **"MIỄN KHÔNG ĐƯỢC NẶNG MÁY"** (Total system RAM < 45MB, CPU idle ~0%, zero Docker/Redis/Prometheus/Grafana).
- Cross-verify and present GPT's recommendations to the User.

## 2. Resource & Footprint Constraints
- Gateway Core: Python stdlib / asyncio (< 15MB RAM).
- Watchdog: Subprocess supervisor (< 1MB RAM).
- Tier-4 Daemon: Go static binary (< 25MB RAM).
- Telemetry: SQLite WAL mode (< 2MB disk).
- Total Footprint Target: < 45MB RAM.

## 3. Anti-Crash Protocol (ACP-V1)
- Strict async timeouts on all network calls.
- Non-blocking state management (no lock held across an await).
- Zero plaintext secret exposure to git history.
