import asyncio
import json
import os
import shutil
import sys
import time
import urllib.request
import websockets

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

TARGET_ID = "4E901E829F8830F38A32B509A1F7C75E"
OBSIDIAN_DIR = r"C:\Users\nswcl\OneDrive\Documents\Obsidian Vault\00_LAR_OS"
LOCAL_CONTEXT_FILE = "SESSION_CONTEXT_SUMMARY.md"

async def harvest():
    print("[1] Connecting to Opera Neon tab to harvest streaming response...")
    with urllib.request.urlopen("http://127.0.0.1:9224/json") as r:
        tabs = json.loads(r.read().decode("utf-8"))
    t = [x for x in tabs if x.get("id") == TARGET_ID][0]
    ws_url = t.get("webSocketDebuggerUrl")

    async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Page.bringToFront"}))
        await asyncio.sleep(0.5)

        start_time = time.time()
        last_text = ""
        stable_count = 0

        while time.time() - start_time < 240:
            await asyncio.sleep(3.0)
            scrape_js = """
            (function() {
                var stopBtn = document.querySelector('button[data-testid="stop-button"], [aria-label*="Dừng"], [aria-label*="Stop"]');
                var turns = Array.from(document.querySelectorAll('div[data-message-author-role="assistant"], article'));
                var lastTurn = turns.length > 0 ? turns[turns.length - 1] : null;
                var text = "";
                if (lastTurn) {
                    var md = lastTurn.querySelector('.markdown') || lastTurn;
                    text = md.innerText.trim();
                }
                return JSON.stringify({
                    is_streaming: Boolean(stopBtn),
                    text: text,
                    turns_count: turns.length
                });
            })()
            """
            scrape_id = int(time.time() * 1000) % 100000
            await ws.send(json.dumps({
                "id": scrape_id,
                "method": "Runtime.evaluate",
                "params": {"expression": scrape_js, "returnByValue": True}
            }))

            data = None
            try:
                while True:
                    raw = await asyncio.wait_for(ws.recv(), 5.0)
                    msg = json.loads(raw)
                    if msg.get("id") == scrape_id:
                        val = msg.get("result", {}).get("result", {}).get("value")
                        if val:
                            data = json.loads(val)
                        break
            except asyncio.TimeoutError:
                continue

            if not data:
                continue

            curr = data.get("text", "")
            streaming = data.get("is_streaming", False)
            print(f"[{round(time.time() - start_time, 1)}s] Streaming: {streaming}, Length: {len(curr)} chars")

            if curr and curr == last_text and not streaming:
                stable_count += 1
                if stable_count >= 2:
                    print(f"\n[✓] Response Generation Completed ({len(curr)} chars)!")
                    with open("chatgpt_hospital_prevention_response.md", "w", encoding="utf-8") as f:
                        f.write(curr)
                    print("[✓] Saved response to chatgpt_hospital_prevention_response.md")
                    
                    sync_to_obsidian(curr)
                    return curr
            else:
                stable_count = 0
                last_text = curr

        if last_text:
            print(f"[!] Timeout reached, capturing final text ({len(last_text)} chars)")
            with open("chatgpt_hospital_prevention_response.md", "w", encoding="utf-8") as f:
                f.write(last_text)
            sync_to_obsidian(last_text)
            return last_text

def sync_to_obsidian(response_text: str):
    print("[2] Updating SESSION_CONTEXT_SUMMARY.md and syncing to Obsidian Vault...")
    summary_content = f"""# LAR-OS & ANTIGRAVITY SESSION CONTEXT SUMMARY
**Updated**: {time.strftime('%Y-%m-%d %H:%M:%S')} (Local Time)
**System Health**: 100% OPERATIONAL | ANTIGRAVITY IDE CURED & DISCHARGED (HOSPITAL.MD)
**LAR-OS State**: Phase 12.1 Nuclear Hardening Complete (Chaos C1 - C14: 20/20 Passed)

---

## 1. Executive Summary & Clinical Record
- **Antigravity IDE v2.5.5 Clinical Discharge**:
  - **Pathology**: Empty window (`MainWindowHandle = 0`), crash in Node ESM bootstrap (`ERR_MODULE_NOT_FOUND` on `out\\main.js`).
  - **Etiology**: 27 zombie `Antigravity IDE.exe` processes held `AntigravityIDEMutex` and locked binary files during auto-update, corrupting extraction.
  - **Intervention**: Killed 27 zombie processes -> Ran in-place silent installer (`/VERYSILENT /SUPPRESSMSGBOXES /NORESTART`) -> Re-established `out\\main.js` (15,040,636 bytes). User profile & extensions 100% intact.
  - **Status**: Discharged. `MainWindowHandle = 11601146`, Language Server connected (PID `29412`), zero crashes.
- **LAR-OS Gateway v3.6 & Nuclear Watcher v3.6**:
  - PID reuse protection via native Windows `kernel32.GetProcessTimes` (`ctypes`).
  - Isolated SOS subprocess execution (`gmail_spark_sender.py --send-sos`).
  - Stale graceful flag handling & heartbeat read hysteresis.
  - Stress Test Suite (Chaos C9 - C14): 6/6 PASSED (100 concurrent requests, p50=731ms, p95=1449ms).
  - Total Chaos Test Suite: 20/20 PASSED (100.0%).

---

## 2. ChatGPT Brainstorming: Preventive Measures ("Phòng Bệnh")
*Consultation conducted via Opera Neon CDP (port 9224) without touching past messages.*

{response_text}

---

## 3. Golden Invariants
- Gateway RAM: < 45MB (Current ~35MB)
- Watcher RAM: < 15MB (Current ~8.4MB)
- Idle CPU: 0.0%
- SQLite: < 2MB (Current ~120KB)
- Zero SaaS / Zero Docker dependencies.
"""

    with open(LOCAL_CONTEXT_FILE, "w", encoding="utf-8") as f:
        f.write(summary_content)
    print(f"  -> Written local {LOCAL_CONTEXT_FILE}")

    if os.path.exists(OBSIDIAN_DIR):
        obsidian_target = os.path.join(OBSIDIAN_DIR, LOCAL_CONTEXT_FILE)
        shutil.copyfile(LOCAL_CONTEXT_FILE, obsidian_target)
        print(f"  -> Successfully synced to Obsidian Vault: {obsidian_target}")
    else:
        print(f"  [!] Obsidian directory {OBSIDIAN_DIR} not found.")

if __name__ == "__main__":
    asyncio.run(harvest())
