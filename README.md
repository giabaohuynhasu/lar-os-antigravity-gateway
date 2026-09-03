---
license: mit
tags:
- lar-os
- ai-gateway
- antigravity
- cloud-cluster
- notebooklm
---

# LAR-OS Antigravity Gateway (v2.0)
**High-Throughput Multi-Account Round-Robin AI Gateway, Cloud Shell Cluster & JIT NotebookLM Authenticator**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-lar--os--antigravity--gateway-blue)](https://hf.co/Jun33550336/lar-os-antigravity-gateway)

---

## 🌟 Executive Overview
**LAR-OS Antigravity Gateway** is an enterprise-grade AI orchestration gateway designed to unify distributed compute, multi-account quota balancing, edge device zero-disk execution, and session-persistent research tooling.

It serves as the runtime backbone for **LAR-OS (Longevity & Asymmetry Research Operating System)**, preventing system bottlenecks, memory leaks, context overflow, and API rate limits.

---

## ⚡ Key Architectural Capabilities

### 1. True Round-Robin Multi-Account Load Balancer (`port 18797`)
- Provides an **OpenAI-compatible `/v1/chat/completions` API**.
- Dynamically cycles sequential requests across multiple Google Pro API accounts (`thuaquan228`, `baohuynhgia0512`, `giabaohuynh0512`, `giabaohuynh.researcher`).
- Features non-blocking asynchronous execution (`asyncio.to_thread`) targeting `gemini-3.5-flash-lite` with automatic HTTP 429 rate-limit backoff and failover.

### 2. Multi-Node Google Cloud Shell Cluster (`cloud_shell_bridge.py`)
- Solves edge hardware storage constraints (such as low-storage Chromebooks or thin clients) by routing heavy workloads to **Google Cloud Shell Linux worker nodes**.
- Zero local disk space consumed on edge hardware (**0 MB local storage footprint**).
- Leverages Google Cloud secure SSH tunneling to run multi-node jobs across:
  - **Node 1**: 4 vCPUs (Intel Xeon @ 2.20GHz), 16 GB RAM (Debian Linux x86_64).
  - **Node 2**: 4 vCPUs (Intel Xeon @ 2.20GHz), 8 GB RAM (Debian Linux x86_64).
- Totaling **24 GB RAM combined cloud compute** at zero infrastructure cost.

### 3. Just-In-Time (JIT) NotebookLM Auto-Authentication (`nlm_safe.py`)
- Eliminates the recurring expiration of Google session cookies (`__Secure-1PSIDTS`).
- **Zero Heartbeat / No Polling**: Operates strictly on-demand. Before executing any notebook query or mutation, verifies credentials via `nlm login --check` in 0.2s.
- If expired, automatically re-authenticates headlessly using the persistent local Chrome profile without requiring user intervention or persistent background daemons.

### 4. Anti-Crash Protocol (ACP-V1) Guard (`anti_crash_guard.py`)
- Automated memory and task lifecycle watchdog.
- Enforces strict limits: max 2 concurrent background tasks, ephemeral sandbox pruning, orphan process termination, and context token slicing ($\le 50$ lines per command output).

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

### 1. Requirements
```bash
pip install -r requirements.txt
```

### 2. Start the Gateway Daemon
```bash
python lar_os_gateway.py
```
The gateway will start on `http://127.0.0.1:18797`.

### 3. Query the Gateway (OpenAI Compatible)
```bash
curl http://127.0.0.1:18797/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer lar-os-master" \
  -d '{
    "model": "gemini-3.5-flash-lite",
    "messages": [{"role": "user", "content": "Ping from LAR-OS Swarm"}]
  }'
```

### 4. Run Multi-Node Cloud Shell Audit
```bash
python cloud_shell_bridge.py
```

### 5. Safe NotebookLM Execution
```bash
python nlm_safe.py notebook list
```

---

## 📄 License & Attribution
- **Author:** Gia Bao Huynh (Jun)
- **ORCID:** [0009-0008-2372-5852](https://orcid.org/0009-0008-2372-5852)
- **Affiliation:** Independent Scholar / Arizona State University
- **License:** MIT License
