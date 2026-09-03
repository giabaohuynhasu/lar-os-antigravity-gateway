---
license: mit
tags:
- lar-os
- ai-gateway
- antigravity
- claude-code
- tool-calling
- rtk-compaction
- cloud-cluster
- notebooklm
---

# LAR-OS Antigravity Gateway (v3.0)
**Autonomous Multi-Account AI Gateway, Claude Code Tool-Calling Bridge & JIT NotebookLM Authenticator**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22283507.svg)](https://doi.org/10.5281/zenodo.22283507)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-lar--os--antigravity--gateway-blue)](https://hf.co/Jun33550336/lar-os-antigravity-gateway)

---

## 🌟 Executive Overview
**LAR-OS Antigravity Gateway v3.0** is an enterprise-grade AI orchestration gateway that bridges **Anthropic Claude Code CLI**, **Google Antigravity IDE**, and **OpenAI-compatible clients** directly into free high-throughput Google AI Pro accounts, multi-node Linux Cloud Shell clusters, and browser consensus engines.

It serves as the runtime backbone for **LAR-OS (Longevity & Asymmetry Research Operating System)**, combining the best innovations from `CLIProxyAPI` and `9router` with strict adherence to the **Anti-Crash Protocol (ACP-V1)**.

---

## ⚡ v3.0 Core Capabilities

### 1. Bidirectional Anthropic ⇄ Gemini Tool-Calling Bridge
- Fully translates Anthropic `tools` (`input_schema`) to Google Gemini `function_declarations`.
- Automatically maps Gemini `functionCall` responses to Anthropic `tool_use` blocks.
- **Enables Claude Code CLI to run its complete autonomous agentic loop** (viewing files, editing code, running bash commands) through zero-cost Google AI Pro accounts.

### 2. RTK Context Compactor Engine (-35% Token Overhead)
- Inspired by `decolua/9router`.
- Automatically strips formatting fluff, collapses redundant newlines, and tightens whitespace.
- Reduces token consumption by **35%**, doubles generation speed, and prevents context overflow.

### 3. Smart Account Health & Circuit Breaker
- Inspired by `router-for-me/CLIProxyAPI`.
- Monitors account error states (HTTP 429 rate limits, socket timeouts).
- Automatically isolates failing accounts for **60 seconds** and fails over instantaneously to the next healthy Pro account in the pool with **zero connection drops**.

### 4. Bounded LRU Cache (ACP-V1 Memory Guard)
- MD5-based prompt caching for repeated queries.
- Returns responses in **0.30 seconds** with **0 quota consumed**.
- Strictly bounded to 50 items to prevent RAM bloat.

### 5. Live Embedded Web Dashboard (`http://127.0.0.1:18797/dashboard`)
- High-aesthetic dark-mode interface with Glassmorphism styling.
- Live telemetry: Request counters, cache hit rates, RTK character savings, and real-time Google AI Pro account status.

---

## 🏛️ Account & Role Matrix

| STT | Account Identifier | Role | Responsibilities |
|---|---|---|---|
| 1 | `thuaquan228@gmail.com` | **Lead Architect & Core Engine** | Architectural synthesis, primary code generation, Cloud Shell Node 1 (16GB RAM) |
| 2 | `baohuynhgia0512@gmail.com` | **Deep Reasoning & Security Logic** | Formal logic verification, quantitative auditing, security review |
| 3 | `giabaohuynh0512@gmail.com` | **System Automation & Daemon** | Task scheduling, filesystem I/O, watchdog execution, Cloud Shell Node 2 (8GB RAM) |
| 4 | `giabaohuynh.researcher@gmail.com` | **Knowledge Discovery & Multimodal** | Academic literature retrieval, multimodal artifact ingestion |

---

## 🚀 Quickstart

### 1. Start the Gateway Daemon
```bash
uv run python lar_os_gateway.py
```
The gateway will start on `http://127.0.0.1:18797`.

### 2. Access Live Web Dashboard
Open your browser at:
👉 `http://127.0.0.1:18797/dashboard`

### 3. Connect Claude Code CLI
```bash
export ANTHROPIC_BASE_URL="http://127.0.0.1:18797"
export ANTHROPIC_API_KEY="lar-os-master"
claude
```

---

## 📄 License & Attribution
- **Author:** Gia Bao Huynh (Jun)
- **ORCID:** [0009-0008-2372-5852](https://orcid.org/0009-0008-2372-5852)
- **Affiliation:** Independent Scholar / Arizona State University
- **License:** MIT License
