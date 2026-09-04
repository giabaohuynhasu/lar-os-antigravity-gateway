"""
LAR-OS Nuclear Watcher Daemon (v3.5 - Out-of-Band Resilience Edition)
Author: Gia Bao Huynh (Jun) / Antigravity

Golden Invariants:
1. G6: Nuclear Watcher MUST live in an independent process outside Gateway.
2. G7: SOS sender MUST NOT depend on Gateway process.
3. G8: One incident produces exactly ONE SOS email (Incident Deduplication).
4. G11: Watcher idle CPU ≈ 0% (sleep-based polling).
5. G13: RAM footprint < 15MB, zero external SaaS / Docker / Prometheus.
"""

import os
import sys
import json
import time
import uuid
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_DIR = Path(__file__).resolve().parent
HEARTBEAT_FILE = WORKSPACE_DIR / "heartbeat.json"
CRASH_LOG = WORKSPACE_DIR / "crash" / "latest.txt"
STATE_FILE = WORKSPACE_DIR / "nuclear_state.json"
RECOVER_SCRIPT = WORKSPACE_DIR / "recover_gateway.ps1"
PYTHON_EXE = WORKSPACE_DIR.parent / ".venv" / "Scripts" / "python.exe"
if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)

HEARTBEAT_MAX_AGE_SEC = 30.0
WATCH_INTERVAL_SEC = 10.0
MAX_AUTO_RESTARTS = 3

class IncidentFSM:
    GREEN = "GREEN"
    DEGRADED = "DEGRADED"
    NUCLEAR = "NUCLEAR"
    RECOVERING = "RECOVERING"
    EXHAUSTED = "EXHAUSTED"

def is_pid_alive(pid: int) -> bool:
    """Windows-safe process liveness check using kernel32 or os.kill."""
    if pid <= 0:
        return False
    if sys.platform.startswith("win"):
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong()
            if ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return exit_code.value == STILL_ACTIVE
            return False
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

def read_atomic_heartbeat() -> Optional[Dict[str, Any]]:
    """Reads Gateway heartbeat atomically."""
    if not HEARTBEAT_FILE.exists():
        return None
    try:
        with open(HEARTBEAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # File might be mid-replace or transiently locked, wait 50ms and retry once
        time.sleep(0.05)
        try:
            with open(HEARTBEAT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

def get_last_forensic_lines(limit: int = 8) -> List[str]:
    """Extracts last N non-empty lines from crash/latest.txt."""
    if not CRASH_LOG.exists():
        return []
    try:
        with open(CRASH_LOG, "r", encoding="utf-8", errors="replace") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            return lines[-limit:] if lines else []
    except Exception:
        return []

class NuclearWatcher:
    def __init__(self, check_interval: float = WATCH_INTERVAL_SEC):
        self.interval = check_interval
        self.state = IncidentFSM.GREEN
        self.active_incident_id: Optional[str] = None
        self.restart_count = 0
        self.last_sos_time: float = 0.0
        self._load_state()

    def _load_state(self):
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.active_incident_id = data.get("active_incident_id")
                    self.state = data.get("state", IncidentFSM.GREEN)
            except Exception:
                pass

    def _save_state(self):
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "state": self.state,
                    "active_incident_id": self.active_incident_id,
                    "restart_count": self.restart_count,
                    "last_sos_time": self.last_sos_time,
                    "updated_at": time.time()
                }, f, indent=2)
        except Exception:
            pass

    async def evaluate_liveness(self) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Evaluates system liveness:
        Returns (Trigger, HeartbeatData)
        Trigger can be: 'HEALTHY', 'GRACEFUL_EXIT', 'PROCESS_DEAD', 'EVENT_LOOP_HANG', 'MISSING_HEARTBEAT'
        """
        hb = read_atomic_heartbeat()
        if hb is None:
            return "MISSING_HEARTBEAT", None

        # Check if Gateway shut down intentionally
        if hb.get("graceful") is True or hb.get("state") == "SHUTDOWN":
            return "GRACEFUL_EXIT", hb

        pid = hb.get("pid", 0)
        ts = hb.get("ts", 0)
        age = time.time() - ts

        # Check Process L1
        alive = is_pid_alive(pid)
        if not alive:
            return "PROCESS_DEAD", hb

        # Check Heartbeat L2
        if age > HEARTBEAT_MAX_AGE_SEC:
            return "EVENT_LOOP_HANG", hb

        return "HEALTHY", hb

    async def dispatch_sos_alert(self, trigger: str, hb: Optional[Dict[str, Any]]):
        """Sends pre-formatted Nuclear SOS email to user via GmailSparkSender."""
        from gmail_spark_sender import GmailSparkSender

        inc_id = self.active_incident_id or f"NUC-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        self.active_incident_id = inc_id

        incident_info = {
            "incident_id": inc_id,
            "trigger": trigger,
            "timestamp_str": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pid": hb.get("pid", "N/A") if hb else "N/A",
            "heartbeat_age_sec": round(time.time() - hb.get("ts", time.time()), 1) if hb else "N/A",
            "last_provider": hb.get("last_provider", "UNKNOWN") if hb else "UNKNOWN",
            "hop": hb.get("last_hop", 0) if hb else 0,
            "ram_mb": hb.get("ram_mb", 35.0) if hb else "N/A",
            "cpu_pct": hb.get("cpu_pct", 0.0) if hb else "0.0",
            "sqlite_bytes": hb.get("sqlite_bytes", 0) if hb else 0,
        }

        forensic = get_last_forensic_lines(8)
        print(f"🚨 [NUCLEAR EVENT TRIGGERED] {trigger} | ID: {inc_id}")
        print(f"   Dispatching SOS alert to thuaquan228@gmail.com via Opera Neon CDP (9224)...")

        sender = GmailSparkSender()
        try:
            res = await sender.send_nuclear_sos_alert(incident_info, forensic)
            print(f"✓ SOS Dispatch Result: {res}")
        except Exception as e:
            print(f"[-] SOS Dispatch Exception: {e}")

        self.last_sos_time = time.time()
        self._save_state()

    def attempt_recovery_restart(self):
        """Bounded restart of Gateway via recover_gateway.ps1 or direct python spawn."""
        if self.restart_count >= MAX_AUTO_RESTARTS:
            print(f"⚠️ [RECOVERY EXHAUSTED] Maximum auto-restarts ({MAX_AUTO_RESTARTS}) reached. Awaiting manual rescue.")
            self.state = IncidentFSM.EXHAUSTED
            self._save_state()
            return

        self.restart_count += 1
        print(f"🛟 [RECOVERY ATTEMPT {self.restart_count}/{MAX_AUTO_RESTARTS}] Launching Gateway recovery...")
        try:
            if sys.platform.startswith("win") and RECOVER_SCRIPT.exists():
                subprocess.Popen(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(RECOVER_SCRIPT)],
                    cwd=str(WORKSPACE_DIR),
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
                )
            else:
                gateway_py = WORKSPACE_DIR / "lar_os_gateway.py"
                subprocess.Popen(
                    [str(PYTHON_EXE), str(gateway_py)],
                    cwd=str(WORKSPACE_DIR),
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
                )
            self.state = IncidentFSM.RECOVERING
            self._save_state()
        except Exception as e:
            print(f"[-] Recovery launch error: {e}")

    async def step(self) -> str:
        """Executes a single check step. Returns current state."""
        trigger, hb = await self.evaluate_liveness()

        if trigger == "HEALTHY":
            if self.state in (IncidentFSM.NUCLEAR, IncidentFSM.RECOVERING, IncidentFSM.EXHAUSTED):
                print(f"✨ [GATEWAY RESTORED] Gateway resumed healthy heartbeat! Closing incident {self.active_incident_id}.")
                self.state = IncidentFSM.GREEN
                self.active_incident_id = None
                self.restart_count = 0
                self._save_state()
            return self.state

        if trigger == "GRACEFUL_EXIT":
            # Normal planned shutdown, do nothing
            return self.state

        # At this point, we have an unhandled crash or event loop hang!
        if self.state != IncidentFSM.NUCLEAR and self.state != IncidentFSM.RECOVERING and self.state != IncidentFSM.EXHAUSTED:
            # First transition into Nuclear -> Send exactly 1 SOS
            self.state = IncidentFSM.NUCLEAR
            self.active_incident_id = f"NUC-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
            self._save_state()
            await self.dispatch_sos_alert(trigger, hb)
            self.attempt_recovery_restart()
        elif self.state == IncidentFSM.RECOVERING:
            # We are waiting for Gateway to come back up
            print(f"⏳ Awaiting Gateway heartbeat recovery (Attempt #{self.restart_count})...")
            # If after 30s still dead, attempt next bounded restart
            if time.time() - self.last_sos_time > (self.restart_count * 15.0):
                self.attempt_recovery_restart()

        return self.state

    async def run_forever(self):
        print("=" * 70)
        print("  LAR-OS NUCLEAR WATCHER DAEMON (OUT-OF-BAND PROTOCOL) ONLINE")
        print(f"  Target: {HEARTBEAT_FILE}")
        print(f"  Max Heartbeat Age: {HEARTBEAT_MAX_AGE_SEC}s | Check Interval: {self.interval}s")
        print(f"  Recipient: thuaquan228@gmail.com (Spark Push)")
        print("=" * 70)

        while True:
            try:
                await self.step()
            except Exception as e:
                print(f"[-] Watcher step exception: {e}")
            await asyncio.sleep(self.interval)

if __name__ == "__main__":
    watcher = NuclearWatcher()
    if "--check-once" in sys.argv:
        res = asyncio.run(watcher.step())
        print(f"Single Check Result: {res}")
    else:
        asyncio.run(watcher.run_forever())
