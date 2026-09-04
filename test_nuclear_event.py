"""
Chaos Test C8: Nuclear Event Protocol & Out-of-Band Watchdog Verification
Tests:
1. Atomic Heartbeat Emitter format and freshness
2. Process liveness check (OpenProcess / PID validation)
3. Crash Forensic blackbox retrieval (crash/latest.txt)
4. State Machine transition to NUCLEAR on simulated crash
5. Incident Deduplication invariant (1 Incident = 1 Alert)
6. Recovery & Incident Closure on fresh heartbeat
"""

import os
import sys
import json
import time
import shutil
import asyncio
from pathlib import Path

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))

from lar_os_nuclear_watcher import (
    NuclearWatcher,
    IncidentFSM,
    is_pid_alive,
    read_atomic_heartbeat,
    get_last_forensic_lines,
    HEARTBEAT_FILE,
    CRASH_LOG,
    STATE_FILE
)

PASSED = "PASS"
FAILED = "FAIL"

def run_test_suite():
    print("=" * 75)
    print("  LAR-OS CHAOS TEST C8: NUCLEAR EVENT & OUT-OF-BAND CRASH WATCHDOG")
    print("=" * 75)
    results = []

    # Backup original heartbeat / state if exists
    hb_backup = None
    if HEARTBEAT_FILE.exists():
        hb_backup = HEARTBEAT_FILE.read_bytes()
    state_backup = None
    if STATE_FILE.exists():
        state_backup = STATE_FILE.read_bytes()

    try:
        # -------------------------------------------------------------
        # TEST 1: PID Liveness Detection
        # -------------------------------------------------------------
        current_pid = os.getpid()
        alive_self = is_pid_alive(current_pid)
        dead_fake = is_pid_alive(999999) # Highly improbable PID
        if alive_self and not dead_fake:
            print(f"[{PASSED}] Test 1: PID Liveness Detection (Self {current_pid}: ALIVE, Fake 999999: DEAD)")
            results.append(("Test 1: PID Detection", True))
        else:
            print(f"[{FAILED}] Test 1: PID Liveness Detection Failed (Self: {alive_self}, Fake: {dead_fake})")
            results.append(("Test 1: PID Detection", False))

        # -------------------------------------------------------------
        # TEST 2: Forensic Logger & Last Lines Retrieval
        # -------------------------------------------------------------
        CRASH_LOG.parent.mkdir(parents=True, exist_ok=True)
        sample_logs = [f"Line {i}: simulated traceback entry" for i in range(15)]
        with open(CRASH_LOG, "w", encoding="utf-8") as f:
            f.write("\n".join(sample_logs) + "\n")

        extracted = get_last_forensic_lines(8)
        if len(extracted) == 8 and extracted[-1] == "Line 14: simulated traceback entry":
            print(f"[{PASSED}] Test 2: Forensic Logger Retrieval (Extracted exactly 8 lines)")
            results.append(("Test 2: Forensic Retrieval", True))
        else:
            print(f"[{FAILED}] Test 2: Forensic Logger Retrieval Failed: {extracted}")
            results.append(("Test 2: Forensic Retrieval", False))

        # -------------------------------------------------------------
        # TEST 3: Fresh Heartbeat -> State GREEN
        # -------------------------------------------------------------
        mock_hb = {
            "pid": current_pid,
            "ts": time.time(),
            "boot_id": "GW-TEST01",
            "state": "SERVING",
            "graceful": False,
            "last_provider": "gemini-3.5-flash-lite",
            "last_hop": 1,
            "active_circuits": 5,
            "ram_mb": 34.2,
            "cpu_pct": 0.0,
            "sqlite_bytes": 102400,
            "uptime_sec": 42
        }
        with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
            json.dump(mock_hb, f, indent=2)

        # Clear state file for clean test
        if STATE_FILE.exists():
            STATE_FILE.unlink()

        watcher = NuclearWatcher(check_interval=0.1)
        trigger, hb_data = asyncio.run(watcher.evaluate_liveness())
        if trigger == "HEALTHY":
            print(f"[{PASSED}] Test 3: Fresh Heartbeat Evaluation (Trigger: HEALTHY, PID: {current_pid})")
            results.append(("Test 3: Fresh Heartbeat", True))
        else:
            print(f"[{FAILED}] Test 3: Fresh Heartbeat Failed: {trigger}")
            results.append(("Test 3: Fresh Heartbeat", False))

        # -------------------------------------------------------------
        # TEST 4: Simulated Process Death -> State NUCLEAR
        # -------------------------------------------------------------
        dead_hb = dict(mock_hb)
        dead_hb["pid"] = 999999 # Simulated dead PID
        with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
            json.dump(dead_hb, f, indent=2)

        # Monkey-patch dispatch_sos_alert to avoid triggering actual email during unit test
        sos_dispatched = []
        async def mock_dispatch(trig, data):
            sos_dispatched.append((trig, watcher.active_incident_id))

        watcher.dispatch_sos_alert = mock_dispatch
        # Disable actual subprocess recovery for this test
        watcher.attempt_recovery_restart = lambda: None

        state_after_crash = asyncio.run(watcher.step())
        if state_after_crash == IncidentFSM.NUCLEAR and len(sos_dispatched) == 1:
            inc_id = watcher.active_incident_id
            print(f"[{PASSED}] Test 4: Crash -> State NUCLEAR (Incident: {inc_id}, SOS dispatched: 1)")
            results.append(("Test 4: Crash Detection & SOS", True))
        else:
            print(f"[{FAILED}] Test 4: Crash Detection Failed (State: {state_after_crash}, SOS: {len(sos_dispatched)})")
            results.append(("Test 4: Crash Detection & SOS", False))

        # -------------------------------------------------------------
        # TEST 5: Incident Deduplication Invariant (No duplicate SOS)
        # -------------------------------------------------------------
        # Step a second time while Gateway is still dead
        asyncio.run(watcher.step())
        if len(sos_dispatched) == 1:
            print(f"[{PASSED}] Test 5: Incident Deduplication (Invariant G8: Exactly 1 SOS per incident)")
            results.append(("Test 5: Incident Deduplication", True))
        else:
            print(f"[{FAILED}] Test 5: Deduplication Failed: Dispatched {len(sos_dispatched)} alerts!")
            results.append(("Test 5: Incident Deduplication", False))

        # -------------------------------------------------------------
        # TEST 6: Event Loop Hang Detection (Heartbeat stale > 30s)
        # -------------------------------------------------------------
        hung_hb = dict(mock_hb)
        hung_hb["ts"] = time.time() - 35.0 # Stale by 35s
        with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
            json.dump(hung_hb, f, indent=2)

        hang_trigger, _ = asyncio.run(watcher.evaluate_liveness())
        if hang_trigger == "EVENT_LOOP_HANG":
            print(f"[{PASSED}] Test 6: Event Loop Hang Detection (Heartbeat age 35s > 30s threshold)")
            results.append(("Test 6: Event Loop Hang", True))
        else:
            print(f"[{FAILED}] Test 6: Hang Detection Failed: {hang_trigger}")
            results.append(("Test 6: Event Loop Hang", False))

        # -------------------------------------------------------------
        # TEST 7: Gateway Restored -> State GREEN & Incident Closed
        # -------------------------------------------------------------
        recovered_hb = dict(mock_hb)
        recovered_hb["ts"] = time.time() # Fresh heartbeat
        recovered_hb["pid"] = current_pid
        with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
            json.dump(recovered_hb, f, indent=2)

        final_state = asyncio.run(watcher.step())
        if final_state == IncidentFSM.GREEN and watcher.active_incident_id is None:
            print(f"[{PASSED}] Test 7: Gateway Restoration & Incident Closure (State: GREEN)")
            results.append(("Test 7: Incident Recovery", True))
        else:
            print(f"[{FAILED}] Test 7: Incident Closure Failed (State: {final_state}, ID: {watcher.active_incident_id})")
            results.append(("Test 7: Incident Recovery", False))

    finally:
        # Restore backups
        if hb_backup is not None:
            HEARTBEAT_FILE.write_bytes(hb_backup)
        elif HEARTBEAT_FILE.exists():
            HEARTBEAT_FILE.unlink()

        if state_backup is not None:
            STATE_FILE.write_bytes(state_backup)
        elif STATE_FILE.exists():
            STATE_FILE.unlink()

    print("=" * 75)
    passed_count = sum(1 for _, ok in results if ok)
    total_count = len(results)
    print(f"  CHAOS TEST C8 SCORE: {passed_count} / {total_count} PASSED ({(passed_count/total_count)*100:.1f}%)")
    print("=" * 75)
    return passed_count == total_count

if __name__ == "__main__":
    success = run_test_suite()
    sys.exit(0 if success else 1)
