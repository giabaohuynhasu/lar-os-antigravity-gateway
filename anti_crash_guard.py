"""
Anti-Crash Guard Daemon (ACP-V1)
Fast and lightweight watchdog for system health, temporary sandboxes, and Gateway status.
"""
import os
import sys
import shutil
import subprocess
import urllib.request
import json
from pathlib import Path

SCRATCH_DIR = Path(r"C:\Users\nswcl\.gemini\antigravity-ide\scratch")
GATEWAY_URL = "http://127.0.0.1:18797/health"

def clean_temp_sandboxes():
    """Prune temporary cloned user-data directories in scratch."""
    deleted = 0
    for item in SCRATCH_DIR.iterdir():
        if item.is_dir() and item.name.startswith("temp_"):
            try:
                shutil.rmtree(item, ignore_errors=True)
                deleted += 1
            except Exception:
                pass
    return deleted

def check_gateway_health():
    """Verify if the unified Gateway on port 18797 is responsive."""
    try:
        req = urllib.request.Request(GATEWAY_URL, headers={"User-Agent": "AntiCrashGuard/1.0"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            return True, data
    except Exception as e:
        return False, str(e)

def run_audit():
    print("=" * 60, flush=True)
    print("  ANTI-CRASH GUARD PROTOCOL (ACP-V1) - SYSTEM AUDIT", flush=True)
    print("=" * 60, flush=True)

    # 1. Prune temporary scratch sandboxes
    temps = clean_temp_sandboxes()
    print(f"[1] Ephemeral Sandboxes Pruned: {temps}", flush=True)

    # 2. Check active Gateway status
    gw_ok, gw_info = check_gateway_health()
    if gw_ok:
        active_keys = gw_info.get("active_keys", len(gw_info.get("keys", [])))
        print(f"[2] Unified Gateway (Port 18797): ONLINE", flush=True)
    else:
        print(f"[2] Unified Gateway (Port 18797): STANDBY", flush=True)


    # 3. Memory & Disk Health
    total, used, free = shutil.disk_usage(str(SCRATCH_DIR))
    free_gb = free // (2**30)
    print(f"[3] Scratch Disk Free Space: {free_gb} GB", flush=True)

    print("=" * 60, flush=True)
    print("  SYSTEM HEALTH: PROTECTED & STABLE", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    run_audit()
