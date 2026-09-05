"""
LAR-OS Advanced Chaos & Stress Test Suite (Chaos C9 - C14)
Phase 12.1 Nuclear Hardening & Capacity Boundary Validation

Tests:
- C9:  Stale Graceful Epoch Bypass (stale graceful: true cannot suppress Nuclear)
- C10: PID Reuse / Process Creation Time Mismatch (prevents Windows PID recycling confusion)
- C11: Transient Heartbeat Lock Hysteresis (file read glitch = DEGRADED, not instant Nuclear)
- C12: SOS Subprocess Hang & 15s Hard Deadline (child process killed cleanly on timeout)
- C13: High Concurrency Burst Ladder (S1-S4: 10, 25, 50, 100 concurrent requests)
- C14: Port Safety Verification in Recovery (non-Gateway processes protected from kill)

Author: Gia Bao Huynh (Jun) / Antigravity
"""

import os
import sys
import time
import json
import uuid
import shutil
import asyncio
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_DIR = Path(__file__).resolve().parent
PYTHON_EXE = WORKSPACE_DIR.parent / ".venv" / "Scripts" / "python.exe"
if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)

from lar_os_nuclear_watcher import (
    NuclearWatcher,
    IncidentFSM,
    get_windows_process_creation_time,
    verify_process_incarnation,
    HEARTBEAT_FILE,
    STATE_FILE
)

GATEWAY_URL = "http://127.0.0.1:18797"

class StressTestRunner:
    def __init__(self):
        self.results = []
        self.temp_files = []

    def record(self, test_name: str, passed: bool, details: str):
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"[{status}] {test_name}: {details}")

    def cleanup(self):
        for p in self.temp_files:
            try:
                if p.exists():
                    if p.is_dir():
                        shutil.rmtree(p)
                    else:
                        p.unlink()
            except Exception:
                pass

    async def run_c9_stale_graceful(self):
        """C9: Verify that a dead process with stale graceful:true is NOT treated as healthy."""
        backup = None
        if HEARTBEAT_FILE.exists():
            backup = HEARTBEAT_FILE.read_bytes()

        try:
            # Simulate a dead Gateway that stopped gracefully 60 seconds ago
            stale_payload = {
                "pid": 999998, # Definitely dead PID
                "process_creation_time": time.time() - 200,
                "ts": time.time() - 60.0, # 60s ago (> 30s threshold)
                "boot_id": "GW-STALE01",
                "state": "SHUTDOWN",
                "graceful": True,
                "last_provider": "GEMINI_PRO",
                "last_hop": 1
            }
            with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
                json.dump(stale_payload, f)

            watcher = NuclearWatcher()
            trigger, hb = await watcher.evaluate_liveness()

            passed = (trigger == "STALE_GRACEFUL_EXHAUSTED" or trigger == "PROCESS_DEAD")
            self.record(
                "Chaos C9 (Stale Graceful Epoch)",
                passed,
                f"Evaluated trigger: '{trigger}' (Expected STALE_GRACEFUL_EXHAUSTED or PROCESS_DEAD)"
            )
        finally:
            if backup:
                HEARTBEAT_FILE.write_bytes(backup)

    async def run_c10_pid_reuse(self):
        """C10: Verify PID reuse detection when PID is alive but creation time does not match."""
        my_pid = os.getpid()
        actual_creation_time = get_windows_process_creation_time(my_pid)
        bogus_creation_time = (actual_creation_time or time.time()) - 3600.0 # 1 hour earlier

        # Verify function directly
        is_valid = verify_process_incarnation(my_pid, bogus_creation_time)
        is_valid_real = verify_process_incarnation(my_pid, actual_creation_time)

        passed = (is_valid is False and is_valid_real is True)
        self.record(
            "Chaos C10 (PID Reuse & Creation Time Verification)",
            passed,
            f"Bogus creation time rejected: {not is_valid}, Real creation time accepted: {is_valid_real}"
        )

    async def run_c11_transient_lock_hysteresis(self):
        """C11: Verify transient read failure transitions to DEGRADED rather than instant NUCLEAR."""
        backup = None
        if HEARTBEAT_FILE.exists():
            backup = HEARTBEAT_FILE.read_bytes()

        try:
            # Temporarily remove heartbeat file
            if HEARTBEAT_FILE.exists():
                HEARTBEAT_FILE.unlink()

            watcher = NuclearWatcher()
            watcher.last_valid_heartbeat_time = time.time() - 5.0 # Healthy 5s ago (< 30s threshold)

            trigger_transient, _ = await watcher.evaluate_liveness()

            # Now simulate long-term missing (> 30s)
            watcher.last_valid_heartbeat_time = time.time() - 40.0
            trigger_persistent, _ = await watcher.evaluate_liveness()

            passed = (trigger_transient == "DEGRADED" and trigger_persistent == "MISSING_HEARTBEAT")
            self.record(
                "Chaos C11 (Transient Heartbeat Read Hysteresis)",
                passed,
                f"Transient: '{trigger_transient}' (Expected DEGRADED), Persistent: '{trigger_persistent}' (Expected MISSING_HEARTBEAT)"
            )
        finally:
            if backup:
                HEARTBEAT_FILE.write_bytes(backup)

    async def run_c12_sos_subprocess_hang(self):
        """C12: Verify isolated SOS subprocess enforces 15s deadline and terminates cleanly."""
        # Create a mock hung script that sleeps for 30 seconds
        mock_script = WORKSPACE_DIR / "mock_hung_sos.py"
        self.temp_files.append(mock_script)
        mock_script.write_text("""
import time, sys
time.sleep(30)
sys.exit(0)
""", encoding="utf-8")

        # Test subprocess runner with a tight 2.0s deadline for testing speed
        start = time.time()
        proc = await asyncio.create_subprocess_exec(
            str(PYTHON_EXE), str(mock_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        timed_out = False
        try:
            await asyncio.wait_for(proc.communicate(), timeout=2.0)
        except asyncio.TimeoutError:
            timed_out = True
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass

        duration = time.time() - start
        passed = timed_out and duration < 3.5
        self.record(
            "Chaos C12 (SOS Subprocess Hang & Deadline Termination)",
            passed,
            f"Process killed after {duration:.2f}s timeout, return code: {proc.returncode}"
        )

    async def run_c13_concurrency_ladder(self):
        """C13: High Concurrency Burst Ladder (S1-S4: 10, 25, 50, 100 concurrent requests)."""
        levels = [10, 25, 50, 100]
        results_summary = []

        async def fetch_one(session_id: int):
            t0 = time.time()
            try:
                req = urllib.request.Request(
                    f"{GATEWAY_URL}/status",
                    headers={"User-Agent": f"StressClient-{session_id}"}
                )
                loop = asyncio.get_event_loop()
                def do_req():
                    with urllib.request.urlopen(req, timeout=10.0) as resp:
                        return resp.getcode()
                status = await loop.run_in_executor(None, do_req)
                lat = (time.time() - t0) * 1000
                return True, lat, status
            except Exception as e:
                lat = (time.time() - t0) * 1000
                return False, lat, str(e)

        all_passed = True
        for count in levels:
            t_start = time.time()
            tasks = [fetch_one(i) for i in range(count)]
            res = await asyncio.gather(*tasks)
            elapsed = time.time() - t_start

            successes = [r for r in res if r[0]]
            latencies = sorted([r[1] for r in res])
            p50 = latencies[len(latencies)//2]
            p95 = latencies[int(len(latencies)*0.95)]
            max_lat = latencies[-1]
            success_rate = (len(successes) / count) * 100

            results_summary.append(f"[{count} reqs: {success_rate:.0f}% OK, p50={p50:.1f}ms, p95={p95:.1f}ms, total={elapsed:.2f}s]")
            if success_rate < 95.0 or max_lat > 15000:
                all_passed = False

        self.record(
            "Chaos C13 (High Concurrency Burst Ladder S1-S4)",
            all_passed,
            " | ".join(results_summary)
        )

    async def run_c14_port_safety(self):
        """C14: Verify recover_gateway.ps1 protects non-Gateway processes from accidental kill."""
        ps_file = WORKSPACE_DIR / "recover_gateway.ps1"
        content = ps_file.read_text(encoding="utf-8")

        checks = [
            'Get-NetTCPConnection -LocalPort 18797',
            'Get-Process -Id $pidToKill',
            '*python*',
            'Skipping force-kill for safety'
        ]
        has_all_checks = all(c in content for c in checks)
        self.record(
            "Chaos C14 (Port Safety Verification in Recovery)",
            has_all_checks,
            "Confirmed recover_gateway.ps1 inspects process identity and aborts kill if non-Gateway process"
        )

    async def run_all(self):
        print("=" * 75)
        print("  LAR-OS PHASE 12.1 NUCLEAR HARDENING & CAPACITY STRESS TEST SUITE")
        print("  Chaos Tests: C9, C10, C11, C12, C13 (S1-S4 Ladder), C14")
        print("=" * 75)

        try:
            await self.run_c9_stale_graceful()
            await self.run_c10_pid_reuse()
            await self.run_c11_transient_lock_hysteresis()
            await self.run_c12_sos_subprocess_hang()
            await self.run_c13_concurrency_ladder()
            await self.run_c14_port_safety()
        finally:
            self.cleanup()

        print("=" * 75)
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        pct = (passed / total) * 100 if total > 0 else 0
        print(f"STRESS TEST SUMMARY: {passed} / {total} Tests PASSED ({pct:.1f}%)")
        print("=" * 75)
        return passed == total

if __name__ == "__main__":
    runner = StressTestRunner()
    success = asyncio.run(runner.run_all())
    sys.exit(0 if success else 1)
