"""
LAR-OS Neon Cloud Substrate & AI Gateway Bridge
Author: Gia Bao Huynh (Jun) / LAR-OS
Integrates:
1. Neon Serverless Postgres (v18.6): Cloud-persisted Immortal Ledger ('Chân Thân')
   - Automatically initializes `antigravity_handoffs` & `research_audit_vault`
   - Persists HMAC-signed state handoffs across all Antigravity & Jules sessions
2. Neon AI Gateway: OpenAI-compatible multi-model routing
"""

import os
import sys
import json
import time
import urllib.request
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None

# Credentials provided by user
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:REDACTED_PASSWORD@ep-odd-art-ayt56ir9.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

DATABASE_URL_POOLED = os.getenv(
    "DATABASE_URL_POOLED",
    "postgresql://REDACTED_USER:REDACTED_PASSWORD@REDACTED_HOST/neondb?sslmode=require"
)

NEON_AUTH_BASE_URL = os.getenv(
    "NEON_AUTH_BASE_URL",
    "https://ep-odd-art-ayt56ir9.neonauth.c-5.us-east-2.aws.neon.tech/neondb/auth"
)

NEON_AI_GATEWAY_BASE_URL = os.getenv(
    "NEON_AI_GATEWAY_BASE_URL",
    "https://br-spring-dust-ayaan640-api.ai.c-5.us-east-2.aws.neon.tech"
)

NEON_AI_GATEWAY_TOKEN = os.getenv(
    "NEON_AI_GATEWAY_TOKEN",
    "REDACTED_TOKEN"
)

def init_neon_database() -> Dict[str, Any]:
    """Initializes the required tables in Neon Serverless Postgres."""
    if not psycopg:
        return {"status": "error", "message": "psycopg is not installed"}

    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                # 1. State handoffs table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS antigravity_handoffs (
                        id SERIAL PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        timestamp TIMESTAMPTZ NOT NULL,
                        signature TEXT NOT NULL,
                        account_email TEXT,
                        payload JSONB NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # 2. Research audits table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS research_audit_vault (
                        id SERIAL PRIMARY KEY,
                        hypothesis TEXT NOT NULL,
                        exit_condition TEXT,
                        external_anchor TEXT,
                        confidence TEXT,
                        source_note TEXT,
                        payload JSONB NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()

        return {"status": "success", "message": "Neon Postgres tables initialized successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def persist_handoff_to_neon(handoff_data: Dict[str, Any]) -> Dict[str, Any]:
    """Persists a cryptographic state handoff into Neon Postgres."""
    if not psycopg:
        return {"status": "error", "message": "psycopg is not installed"}

    try:
        session_id = handoff_data.get("session_id", f"session-{int(time.time())}")
        sig = handoff_data.get("signature", "")
        acc = handoff_data.get("state", {}).get("account", {}).get("email", "")

        with psycopg.connect(DATABASE_URL, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO antigravity_handoffs (session_id, timestamp, signature, account_email, payload)
                    VALUES (%s, NOW(), %s, %s, %s)
                    RETURNING id, created_at;
                """, (session_id, sig, acc, json.dumps(handoff_data)))
                row = cur.fetchone()
                conn.commit()
                return {
                    "status": "success",
                    "id": row[0] if row else None,
                    "created_at": str(row[1]) if row else None
                }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def fetch_latest_handoff_from_neon() -> Optional[Dict[str, Any]]:
    """Retrieves the latest verified state handoff from Neon Postgres."""
    if not psycopg:
        return None

    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=10, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, session_id, timestamp, signature, account_email, payload
                    FROM antigravity_handoffs
                    ORDER BY id DESC
                    LIMIT 1;
                """)
                row = cur.fetchone()
                if row:
                    payload = row["payload"]
                    if isinstance(payload, str):
                        payload = json.loads(payload)
                    return payload
                return None
    except Exception:
        return None

def persist_audit_to_neon(record_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Persists a Third-Order Audit record into Neon Postgres."""
    if not psycopg:
        return {"status": "error", "message": "psycopg is not installed"}

    try:
        hyp = record_dict.get("hypothesis", "")
        exit_c = record_dict.get("stated_exit_condition", "")
        anchor = record_dict.get("external_anchor", "")
        conf = record_dict.get("confidence", "HIGH")
        note = record_dict.get("source_note", "")

        with psycopg.connect(DATABASE_URL, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO research_audit_vault (hypothesis, exit_condition, external_anchor, confidence, source_note, payload)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (hyp, exit_c, anchor, conf, note, json.dumps(record_dict)))
                row = cur.fetchone()
                conn.commit()
                return {"status": "success", "id": row[0] if row else None}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def query_neon_ai_gateway(prompt: str, model: str = "claude-3-5-sonnet") -> Dict[str, Any]:
    """Queries Neon AI Gateway via standard OpenAI-compatible API."""
    url = f"{NEON_AI_GATEWAY_BASE_URL.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {NEON_AI_GATEWAY_TOKEN}"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {
                "status": "success",
                "model": data.get("model", model),
                "response": content,
                "usage": data.get("usage", {})
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
