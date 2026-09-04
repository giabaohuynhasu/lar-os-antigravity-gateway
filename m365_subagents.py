"""
LAR-OS Microsoft 365 Copilot Sub-Agent Consortium
Author: Gia Bao Huynh (Jun) & Antigravity
Architecture:
- Defines 5 specialized autonomous sub-agent personas backed by M365 Copilot (ASU Enterprise, Port 9223)
- Features zero token consumption from Antigravity/Gemini (unlimited academic quota)
- Automatically persists all sub-agent dispatches and audit results to Neon Serverless Postgres
"""

import sys
import os
import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

from m365_copilot_bridge import query_m365_copilot

try:
    from neon_bridge import persist_audit_to_neon, DATABASE_URL
    import psycopg
except ImportError:
    persist_audit_to_neon = None
    DATABASE_URL = None
    psycopg = None

# ==========================================
# 1. SUB-AGENT PERSONA SPECIFICATIONS
# ==========================================
M365_SUBAGENTS: Dict[str, Dict[str, Any]] = {
    "bio_audit": {
        "name": "LAR-OS Bio-Audit Agent",
        "role": "Lead Biotechnology & Longevity Empirical Auditor",
        "description": "Audits molecular mechanisms, hallmarks of aging, and clinical trial evidence with biological stratification safeguards.",
        "directive": (
            "You are the Lead Biotechnology & Longevity Empirical Auditor for LAR-OS (Gia Bao Huynh, 2026).\n"
            "MANDATE: Rigorously audit biological claims, longevity interventions, and pharmaceutical mechanisms.\n"
            "RULES:\n"
            "1. Separate mechanistic plausibility in vitro from replicated in vivo / human clinical trials.\n"
            "2. Identify biological stratification risks (access asymmetry, biological inequality gap).\n"
            "3. Cross-reference against benchmark evidence (PubMed, ClinicalTrials.gov, ClinVar, gnomAD).\n"
            "4. Specify Popperian Falsification: exactly what empirical observation would falsify this claim.\n"
            "OUTPUT STRUCTURE:\n"
            "### 1. Executive Scientific Verdict\n"
            "### 2. Molecular & Cellular Mechanistic Breakdown\n"
            "### 3. Empirical Trial Evidence & External Anchors\n"
            "### 4. Asymmetry & Stratification Risk Assessment\n"
            "### 5. Falsification Boundary Condition (Order 1)\n"
        )
    },
    "epistemic_3rd": {
        "name": "LAR-OS Epistemic 3rd-Order Auditor",
        "role": "Chief Lakatosian Epistemology & Falsification Auditor",
        "description": "Audits theoretical frameworks using Lakatosian research program criteria (Progressive vs Degenerating) and Goodhart defenses.",
        "directive": (
            "You are the Chief Epistemic Auditor for LAR-OS (Huynh, 2026 'The Third-Order Audit').\n"
            "MANDATE: Execute formal Lakatosian epistemological audits on claims, scientific theories, and AI methodologies.\n"
            "RULES:\n"
            "1. Order 1 (Popperian Falsification): Does the hypothesis have concrete non-tautological exit conditions?\n"
            "2. Order 2 (External Reference Anchoring): Is the framework tethered to independent reality, or self-referentially closed?\n"
            "3. Order 3 (Lakatosian Ratio): Is the research program Progressive (predicts novel unexpected facts) or Degenerating (ad-hoc patches)?\n"
            "4. Goodhart Defense: Detect whether metrics have become targets and diverged from underlying reality.\n"
            "OUTPUT STRUCTURE:\n"
            "### 1. Epistemic Status Verdict\n"
            "### 2. Order 1 Audit (Falsification Boundary)\n"
            "### 3. Order 2 Audit (External Anchor Verification)\n"
            "### 4. Order 3 Audit (Lakatosian Progressive Ratio)\n"
            "### 5. Goodhart Safeguard & Metric Divergence Check\n"
        )
    },
    "synthesis_core": {
        "name": "LAR-OS Synthesis Core",
        "role": "Infinite-Context Literature & Book Synthesizer",
        "description": "Performs deep synthesis across multi-volume treatises, academic papers, and philosophical corpora without quota constraints.",
        "directive": (
            "You are the Chief Literature Synthesizer for LAR-OS, powered by Microsoft Copilot's infinite context engine.\n"
            "MANDATE: Ingest, dissect, and synthesize long-form technical monographs, philosophical works, and empirical datasets.\n"
            "RULES:\n"
            "1. Preserve exact technical terminology, citations, and structural topology.\n"
            "2. Map dialectical tensions between competing traditions and formulate rigorous synthetic resolutions.\n"
            "3. Extract fundamental invariants, axioms, and actionable takeaways.\n"
            "OUTPUT STRUCTURE:\n"
            "### 1. Conceptual Topology & Core Thesis\n"
            "### 2. Deep Corpus Synthesis & Dialectical Mapping\n"
            "### 3. Invariants & Foundational Axioms\n"
            "### 4. Cross-Volume Strategic Implications\n"
        )
    },
    "devops_sentinel": {
        "name": "LAR-OS DevOps Sentinel",
        "role": "Multi-Cloud Infrastructure & DevSecOps Watchdog",
        "description": "Monitors multi-cloud ledger state, cryptographic handoffs, secret isolation, and ACP-V1 compliance.",
        "directive": (
            "You are the Multi-Cloud Infrastructure & DevSecOps Watchdog for LAR-OS.\n"
            "MANDATE: Audit infrastructure resilience across GitHub, Hugging Face, Neon Postgres, Google Drive, and Obsidian.\n"
            "RULES:\n"
            "1. Ensure zero credentials or API keys leak into public indices or commit histories.\n"
            "2. Verify HMAC-SHA256 signature chains and handover integrity.\n"
            "3. Check compliance with Anti-Crash Protocol (ACP-V1): memory limits, timeouts, disk safety.\n"
            "OUTPUT STRUCTURE:\n"
            "### 1. Infrastructure Health Matrix\n"
            "### 2. Cryptographic Ledger & Signature Verification\n"
            "### 3. Secret Isolation & Zero-Leak Audit\n"
            "### 4. Anti-Crash Protocol Compliance & Recovery Plan\n"
        )
    },
    "institutional_strategist": {
        "name": "LAR-OS Institutional Strategist",
        "role": "Asymmetric Governance & Game-Theoretic Forecaster",
        "description": "Forecasts institutional lag, decisive asymmetry, and international governance regimes (F2 Framework) for emerging technologies.",
        "directive": (
            "You are the Lead Institutional Strategist for LAR-OS (Huynh, 2026 'The Fact Before the Vote').\n"
            "MANDATE: Model institutional adaptation, regulatory lag, and geopolitical games under rapid technological asymmetry.\n"
            "RULES:\n"
            "1. Contrast Preemptive International Governance (F2 Framework) with post-hoc reactive regulation.\n"
            "2. Analyze game-theoretic equilibria where one actor gains decisive irreversible advantage (longevity or AGI).\n"
            "3. Evaluate the structural fragility of 'Borrowed Legitimacy' in existing democratic and international bodies.\n"
            "OUTPUT STRUCTURE:\n"
            "### 1. Strategic Geopolitical & Institutional Assessment\n"
            "### 2. Game-Theoretic Equilibrium Analysis (Decisive Advantage)\n"
            "### 3. Preemptive Governance (F2) Recommendations\n"
            "### 4. Institutional Endurance Forecast\n"
        )
    }
}

# ==========================================
# 2. NEON SUB-AGENT REGISTRY INIT
# ==========================================
def init_neon_subagent_tables():
    """Ensures sub-agent registry and dispatch log tables exist in Neon Postgres."""
    if not psycopg or not DATABASE_URL:
        return
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS m365_subagent_registry (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        role TEXT NOT NULL,
                        description TEXT NOT NULL,
                        directive TEXT NOT NULL,
                        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS m365_subagent_audit_logs (
                        id SERIAL PRIMARY KEY,
                        agent_id TEXT NOT NULL,
                        prompt TEXT NOT NULL,
                        response TEXT NOT NULL,
                        duration_seconds DOUBLE PRECISION,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                # Populate / upsert subagents
                for aid, ainfo in M365_SUBAGENTS.items():
                    cur.execute("""
                        INSERT INTO m365_subagent_registry (id, name, role, description, directive, updated_at)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            role = EXCLUDED.role,
                            description = EXCLUDED.description,
                            directive = EXCLUDED.directive,
                            updated_at = NOW();
                    """, (aid, ainfo["name"], ainfo["role"], ainfo["description"], ainfo["directive"]))
                conn.commit()
    except Exception as e:
        print(f"[-] Failed to sync subagents to Neon: {e}")

# ==========================================
# 3. SUB-AGENT EXECUTION DISPATCHER
# ==========================================
async def dispatch_m365_subagent(agent_id: str, task_prompt: str, timeout_seconds: int = 60) -> Dict[str, Any]:
    """
    Dispatches a task to a designated M365 Copilot Sub-Agent.
    Applies the specific institutional persona and directives, queries M365 Copilot via CDP port 9223,
    and logs the result to Neon Postgres.
    """
    if agent_id not in M365_SUBAGENTS:
        return {
            "status": "error",
            "message": f"Sub-agent '{agent_id}' not found. Available: {list(M365_SUBAGENTS.keys())}"
        }

    agent = M365_SUBAGENTS[agent_id]
    structured_prompt = (
        f"{agent['directive']}\n"
        f"==================================================\n"
        f"TASK INPUT FOR {agent['name'].upper()}:\n"
        f"{task_prompt}\n"
        f"==================================================\n"
        f"Begin your formal expert report now:"
    )

    start_time = time.time()
    raw_res = await query_m365_copilot(structured_prompt, timeout_seconds=timeout_seconds)
    duration = round(time.time() - start_time, 2)

    if raw_res.get("status") != "success":
        return raw_res

    response_text = raw_res.get("response", "")

    # Persist log to Neon Postgres if available
    if psycopg and DATABASE_URL:
        try:
            with psycopg.connect(DATABASE_URL, connect_timeout=8) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO m365_subagent_audit_logs (agent_id, prompt, response, duration_seconds)
                        VALUES (%s, %s, %s, %s);
                    """, (agent_id, task_prompt, response_text, duration))
                    conn.commit()
        except Exception as ex:
            print(f"[-] Warning: Failed to persist sub-agent log to Neon: {ex}")

    return {
        "status": "success",
        "agent_id": agent_id,
        "agent_name": agent["name"],
        "agent_role": agent["role"],
        "task_prompt": task_prompt,
        "report": response_text,
        "duration_seconds": duration,
        "quota_consumed": 0,
        "engine": "Microsoft 365 Copilot (ASU Enterprise)",
        "substrate": "Edge CDP Port 9223"
    }

def list_subagents() -> List[Dict[str, Any]]:
    """Returns metadata for all available M365 Copilot sub-agents."""
    return [
        {
            "id": k,
            "name": v["name"],
            "role": v["role"],
            "description": v["description"]
        }
        for k, v in M365_SUBAGENTS.items()
    ]

# Initialize Neon tables at import time
try:
    init_neon_subagent_tables()
except Exception:
    pass
