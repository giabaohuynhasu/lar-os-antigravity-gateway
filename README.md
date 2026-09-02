# ⚡ LAR-OS Unified AI Gateway: Antigravity-First Dual-Protocol Proxy

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

> **Non-destructive, dual-protocol AI model proxy designed for Google Antigravity IDE, Tencent WorkBuddy AI, and Claude Code CLI.**  
> Built by **Gia Bao Huynh (Jun)** under the **LAR-OS High-Throughput Multi-Agent Swarm Architecture**.

---

## 🌟 Executive Overview

While existing community solutions rely on reverse-engineering and patching Google Antigravity's internal Electron binaries (which break upon every auto-update) or target only Claude Code CLI, **LAR-OS Unified AI Gateway** introduces an architectural synthesis:

1. **Non-Destructive Skeleton:** Runs as an external, high-performance async proxy server (`FastAPI / Uvicorn`) on localhost port `18797`. Zero binary patching, zero system crashes, 100% update-immune.
2. **Dual-Protocol Endpoints:**
   - **OpenAI Compatible (`/v1/chat/completions`, `/v1/models`):** Natively plugs into Antigravity IDE's official "Add Model" setting and Tencent WorkBuddy AI.
   - **Anthropic Compatible (`/v1/messages`):** Seamlessly routes traffic from Anthropic's `claude-code` CLI.
3. **Multi-Tier Hybrid Backends:**
   - **Tier 1:** Local **Google Gemini** integration (via `google-genai` SDK or Chrome CDP port 9224 with 1M-2M context).
   - **Tier 2:** **Zero-Quota Quad-Browser AI Consortium** (`Comet:9222`, `Edge:9223`, `Chrome:9224`, `Opera Neon:9225`) executing multi-engine parallel consensus across Perplexity, Copilot, Gemini, and ChatGPT.
   - **Tier 3:** Free Cloud AI Tiers (NVIDIA NIM 1,000 RPD, OpenRouter Free, Groq).

---

## 🏛️ System Architecture

```
                      Gia Bao Huynh (Jun) / LAR-OS
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
  [Antigravity IDE & WorkBuddy]                       [Claude Code CLI]
    (OpenAI /v1/chat/completions)                      (Anthropic /v1/messages)
         │                                                   │
         └─────────────────────────┬─────────────────────────┘
                                   │ Port 18797
                                   ▼
         ┌───────────────────────────────────────────────────┐
         │          ⚡ LAR-OS UNIFIED AI GATEWAY             │
         │   (Async FastAPI • Protocol Translator • Cache)   │
         └─────────────────────────┬─────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
  [Google Gemini API]    [Quad-Browser Consortium]     [Cloud Free Tiers]
 • 1.500 RPD Free Tier    • Comet (Perplexity: 9222)   • NVIDIA NIM (1.000 RPD)
 • 1M-2M Context Window   • Edge (Copilot 4o: 9223)    • OpenRouter Free Tiers
 • Zero-Token CDP Bridge  • Chrome (Gemini: 9224)      • Groq Cloud Llama 3.3
                          • Opera Neon (ChatGPT: 9225)
```

---

## 🚀 Quickstart

### 1. Installation & Launch
```bash
git clone https://github.com/giabaohuynhasu/lar-os-antigravity-gateway.git
cd lar-os-antigravity-gateway

# Run via uv (recommended):
uv run --with fastapi --with uvicorn python lar_os_gateway.py
```

The gateway immediately listens on:
- Health Check: `http://127.0.0.1:18797/health`
- Models List: `http://127.0.0.1:18797/v1/models`
- OpenAI Chat: `http://127.0.0.1:18797/v1/chat/completions`
- Anthropic Messages: `http://127.0.0.1:18797/v1/messages`

---

## 🔌 Client Setup

### A. Antigravity IDE & Tencent WorkBuddy AI
Open Settings → **Add Model (OpenAI-compatible)**:
- **Provider:** `OpenAI-compatible`
- **Base URL:** `http://127.0.0.1:18797/v1`
- **API Key:** `lar-os-master`
- **Model Name:** `gemini-2.5-flash` or `deepseek-r1-quad`

### B. Claude Code CLI
Point the Anthropic CLI directly to the Gateway:
```powershell
$env:ANTHROPIC_BASE_URL="http://127.0.0.1:18797"
$env:ANTHROPIC_API_KEY="lar-os-master"
claude
```

---

## 🏆 Attribution & Credits

This architectural design synthesizes and builds upon groundbreaking foundational ideas from the open-source community:

1. **[vahapogut](https://github.com/vahapogut)** (Creator of [`antigravity-add-model`](https://github.com/vahapogut/antigravity-add-model)):
   - *Inspiration:* Pioneered the concept of extending Google Antigravity with external LLM providers and custom model picker interfacing.
2. **[Alishahryar1](https://github.com/Alishahryar1)** (Creator of [`free-claude-code`](https://github.com/Alishahryar1/free-claude-code)):
   - *Inspiration:* Pioneered the clean local proxy pattern translating Anthropic Messages API into free backends with streaming and tool usage.

LAR-OS Gateway merges these two paradigms into a non-destructive, enterprise-grade unified architecture.

---

## 📄 License

Released under the [MIT License](LICENSE).  
Copyright (c) 2026 **Gia Bao Huynh (Jun)** & **LAR-OS Research Foundation**.
