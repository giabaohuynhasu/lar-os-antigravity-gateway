# ANTIGRAVITY CONTINUITY PROTOCOL (AHCP-V1)
## Universal Agent Handoff, State Preservation & Cryptographic Signature Specification

**Protocol Version:** 1.0.0-PRO  
**Author:** Gia Bao Huynh (Jun) · Antigravity Research OS  
**Source of Truth:** GitHub (`giabaohuynhasu/lar-os-antigravity-gateway`) & Hugging Face (`Jun33550336/lar-os-antigravity-gateway`)  
**Persistent Storage:** Google Drive (`G:\Drive của tôi\LAR_OS_Gateway_v3\`) & Obsidian Vault  

---

## 1. Objective & Philosophy

When an active Google Antigravity session (such as `thuaquan228@gmail.com`) approaches quota exhaustion or session cutoff, the **Antigravity Handoff & Continuity Protocol (AHCP-V1)** guarantees a 100% loss-free, seamless transition to an incoming Antigravity instance (`giabaohuynh0512`, `baohuynhgia0512`, `junax2288`, or any new account).

The incoming Antigravity agent will:
1. Ingest the full conversational context, architectural state, active background tasks, and credentials safely.
2. Adopt the exact same tone, chief orchestrator authority, and scientific rigor (Anti-Crash Protocol ACP-V1, War Correspondent discipline, Zero Fabrication).
3. Log its own instance identifier, timestamp, and cryptographic signature in the handover chain.
4. Continue coordinating Google Jules without any interruption or duplicate work.

---

## 2. Cryptographic Instance Identification & Handover Chain

Each Antigravity instance operates with an assigned instance designation:

| Designation | Default Account | Role |
|---|---|---|
| `AGY-ORCHESTRATOR-TQ228` | `thuaquan228@gmail.com` | Founding Chief Orchestrator (Origin) |
| `AGY-ORCHESTRATOR-BH051` | `baohuynhgia0512@gmail.com` | Deep Reasoning & Audit Orchestrator |
| `AGY-ORCHESTRATOR-GB12P` | `giabaohuynh0512@gmail.com` | Systems Automation & Process Orchestrator |
| `AGY-ORCHESTRATOR-JX228` | `junax2288@gmail.com` | Dynamic Pro Reserve Orchestrator |
| `AGY-ORCHESTRATOR-EXT01` | *External / Secondary* | Standby Plugin Instance |

Every state snapshot contains:
* `source_instance`: Instance generating the handoff.
* `timestamp`: ISO-8601 UTC timestamp.
* `state_sequence`: Monotonically increasing sequence number.
* `payload_sha256`: SHA-256 digest of the serialized context and task registry.
* `signature`: HMAC-SHA256 signature validating state provenance.

---

## 3. The Shared Tri-Repository State Plane

```
                      ┌────────────────────────────────────────┐
                      │             STATE PLANE                │
                      │  - STATE_HANDOFF.json                  │
                      │  - CONTINUITY_PROMPT.md                │
                      └──────────────────┬─────────────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 ▼                       ▼                       ▼
       ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
       │   GitHub Repo    │    │ HuggingFace Repo │    │   Google Drive   │
       │  (origin main)   │    │    (hf main)     │    │ (Desktop Mirror) │
       └─────────┬────────┘    └─────────┬────────┘    └─────────┬────────┘
                 │                       │                       │
                 └───────────────────────┼───────────────────────┘
                                         │
                      ┌──────────────────▼─────────────────────┐
                      │   GOOGLE JULES (Autonomous Custodian)  │
                      │   - Verifies PRs & syncs state         │
                      │   - Preserves worker pipeline          │
                      └────────────────────────────────────────┘
```

---

## 4. Google Jules Role During Transitions

Google Jules acts as the **Autonomous State Custodian & Relay Worker**:
1. Jules continues background code generation and testing while Antigravity instances switch.
2. Jules reads `STATE_HANDOFF.json` to verify current active branch, latest test status, and remaining work items.
3. Jules has full access to Google AI Studio via `google_ai_studio_client.py` and maintains autonomous execution loops.

---

## 5. Instant Plug-in Instructions for Incoming Antigravity

When starting a new Antigravity session, the user pastes the content of [`CONTINUITY_PROMPT.md`](file:///C:/Users/nswcl/.gemini/antigravity-ide/scratch/lar-os-antigravity-gateway/CONTINUITY_PROMPT.md) or runs:

```powershell
python antigravity_state_bridge.py --resume
```

The incoming agent will:
1. Validate the cryptographic signature in `STATE_HANDOFF.json`.
2. Acknowledge handover by appending its signature to `HANDOVER_LEDGER.jsonl`.
3. Pick up the highest-priority pending task seamlessly.
