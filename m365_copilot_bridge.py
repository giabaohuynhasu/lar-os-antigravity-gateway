"""
LAR-OS M365 Copilot Infinite Substrate Bridge
Author: Gia Bao Huynh (Jun) & Antigravity
Role: Harness Microsoft 365 Copilot (ASU Educational License) via CDP port 9223
      to farm context, perform zero-quota reasoning, and orchestrate custom agents.
"""

import asyncio
import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

import websockets

CDP_HOST = "127.0.0.1"
CDP_PORT = 9223
COPILOT_HOME_URL = "https://copilot.microsoft.com/"


def is_cdp_alive(port: int = CDP_PORT) -> bool:
    try:
        url = f"http://{CDP_HOST}:{port}/json"
        req = urllib.request.Request(url, headers={"User-Agent": "LAR-OS-Bridge"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def get_copilot_tab(port: int = CDP_PORT) -> Optional[Dict[str, Any]]:
    try:
        url = f"http://{CDP_HOST}:{port}/json"
        req = urllib.request.Request(url, headers={"User-Agent": "LAR-OS-Bridge"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            tabs = json.loads(resp.read().decode("utf-8"))
        
        # Prioritize open copilot tab
        copilot_tabs = [t for t in tabs if "copilot.microsoft.com" in t.get("url", "") and t.get("type") == "page"]
        if copilot_tabs:
            return copilot_tabs[0]
        
        # Fallback to any general page tab
        page_tabs = [t for t in tabs if t.get("type") == "page"]
        return page_tabs[0] if page_tabs else None
    except Exception as e:
        print(f"[-] Error querying CDP tabs: {e}")
        return None


async def query_m365_copilot(prompt: str, timeout_seconds: int = 60) -> Dict[str, Any]:
    """
    Submits a query to Microsoft Copilot via CDP port 9223,
    streams and captures the complete synthesized answer.
    """
    if not is_cdp_alive():
        return {
            "status": "error",
            "message": f"Edge CDP daemon is not reachable on port {CDP_PORT}. Ensure edge_cdp_daemon.py is running."
        }

    tab = get_copilot_tab()
    if not tab:
        return {"status": "error", "message": "No active Copilot or browser page tab found."}

    ws_url = tab.get("webSocketDebuggerUrl")
    if not ws_url:
        return {"status": "error", "message": "Tab does not have webSocketDebuggerUrl."}

    start_time = time.time()

    async with websockets.connect(ws_url) as ws:
        # 1. Dismiss any overlay cookie consent if present
        dismiss_script = """
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const acceptBtn = btns.find(b => b.innerText.includes('Chấp nhận') || b.innerText.includes('Accept'));
            if (acceptBtn) { acceptBtn.click(); return true; }
            return false;
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": dismiss_script}}))
        await ws.recv()

        # 2. Focus textarea
        focus_script = """
        (() => {
            const ta = document.querySelector('textarea');
            if (ta) { ta.focus(); return true; }
            return false;
        })()
        """
        await ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {"expression": focus_script}}))
        await ws.recv()

        # 3. Native CDP Keystroke input
        await ws.send(json.dumps({
            "id": 3,
            "method": "Input.insertText",
            "params": {"text": prompt}
        }))
        await ws.recv()
        await asyncio.sleep(0.3)

        # 4. Dispatch Hardware Enter key
        await ws.send(json.dumps({
            "id": 4,
            "method": "Input.dispatchKeyEvent",
            "params": {
                "type": "keyDown",
                "key": "Enter",
                "code": "Enter",
                "windowsVirtualKeyCode": 13,
                "nativeVirtualKeyCode": 13
            }
        }))
        await ws.recv()
        await ws.send(json.dumps({
            "id": 5,
            "method": "Input.dispatchKeyEvent",
            "params": {
                "type": "keyUp",
                "key": "Enter",
                "code": "Enter",
                "windowsVirtualKeyCode": 13,
                "nativeVirtualKeyCode": 13
            }
        }))
        await ws.recv()

        # 5. Poll response with backoff until completed
        extracted_answer = ""
        prev_len = 0
        stable_count = 0

        for poll_idx in range(timeout_seconds // 2):
            await asyncio.sleep(2)
            check_script = """
            (() => {
                const body = document.body ? document.body.innerText : '';
                const stopBtn = document.querySelector('button[aria-label*="Dừng"], button[aria-label*="Stop"]');
                return JSON.stringify({
                    len: body.length,
                    isGenerating: !!stopBtn,
                    text: body
                });
            })()
            """
            await ws.send(json.dumps({"id": 100 + poll_idx, "method": "Runtime.evaluate", "params": {"expression": check_script}}))
            raw = await ws.recv()
            info = json.loads(json.loads(raw).get("result", {}).get("result", {}).get("value", "{}"))
            
            cur_len = info.get("len", 0)
            is_generating = info.get("isGenerating", False)

            if cur_len == prev_len and cur_len > 300:
                stable_count += 1
            else:
                stable_count = 0
            prev_len = cur_len

            if (not is_generating and stable_count >= 2) or (poll_idx > 5 and not is_generating):
                full_body = info.get("text", "")
                # Extract conversational turn
                extracted_answer = full_body
                break

        duration = round(time.time() - start_time, 2)
        return {
            "status": "success",
            "prompt": prompt,
            "response": extracted_answer,
            "duration_seconds": duration,
            "quota_consumed": 0,  # Completely free unlimited educational quota
            "engine": "Microsoft 365 Copilot (ASU Enterprise)",
            "substrate": "Edge CDP Port 9223"
        }


if __name__ == "__main__":
    test_p = "Nghiên cứu LAR-OS: Tóm tắt 1 vai trò quan trọng của telomere đối với lão hóa tế bào."
    if len(sys.argv) > 1:
        test_p = " ".join(sys.argv[1:])
    res = asyncio.run(query_m365_copilot(test_p))
    print(json.dumps(res, ensure_ascii=False, indent=2))
