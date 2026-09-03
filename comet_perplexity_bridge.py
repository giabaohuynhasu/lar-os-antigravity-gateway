"""
LAR-OS Perplexity Comet Infinite Substrate Bridge
Author: Gia Bao Huynh (Jun) & Antigravity
Role: Harness Perplexity Comet Browser via CDP port 9225
      to farm web research, citation synthesis, and deep literature grounding.
"""

import asyncio
import json
import os
import sys
import time
import urllib.request
from typing import Dict, Any, Optional

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

import websockets

COMET_CDP_HOST = "127.0.0.1"
COMET_CDP_PORT = 9225
PERPLEXITY_HOME_URL = "https://www.perplexity.ai/"


def is_comet_cdp_alive(port: int = COMET_CDP_PORT) -> bool:
    try:
        url = f"http://{COMET_CDP_HOST}:{port}/json"
        req = urllib.request.Request(url, headers={"User-Agent": "LAR-OS-Comet-Bridge"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def get_perplexity_tab(port: int = COMET_CDP_PORT) -> Optional[Dict[str, Any]]:
    try:
        url = f"http://{COMET_CDP_HOST}:{port}/json"
        req = urllib.request.Request(url, headers={"User-Agent": "LAR-OS-Comet-Bridge"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            tabs = json.loads(resp.read().decode("utf-8"))
        
        # Prioritize perplexity page tab
        target_tabs = [t for t in tabs if "perplexity.ai" in t.get("url", "") and t.get("type") == "page"]
        if target_tabs:
            return target_tabs[0]
        
        # Fallback to any general page tab
        page_tabs = [t for t in tabs if t.get("type") == "page"]
        return page_tabs[0] if page_tabs else None
    except Exception as e:
        print(f"[-] Error querying Comet CDP tabs: {e}")
        return None


async def query_perplexity_comet(prompt: str, timeout_seconds: int = 60) -> Dict[str, Any]:
    """
    Submits a research query to Perplexity inside the Comet browser via CDP port 9225,
    streams web citations and captures the synthesized research report.
    """
    if not is_comet_cdp_alive():
        return {
            "status": "error",
            "message": f"Comet CDP daemon is not reachable on port {COMET_CDP_PORT}. Ensure comet_cdp_daemon.py is running."
        }

    tab = get_perplexity_tab()
    if not tab:
        return {"status": "error", "message": "No active Perplexity tab found in Comet browser."}

    ws_url = tab.get("webSocketDebuggerUrl")
    if not ws_url:
        return {"status": "error", "message": "Comet tab does not expose webSocketDebuggerUrl."}

    start_time = time.time()

    async with websockets.connect(ws_url) as ws:
        # 1. Focus input
        focus_script = """
        (() => {
            const el = document.querySelector('div[contenteditable="true"], textarea');
            if (el) { el.focus(); return true; }
            return false;
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": focus_script}}))
        await ws.recv()

        # 2. Native CDP Text Insertion
        await ws.send(json.dumps({
            "id": 2,
            "method": "Input.insertText",
            "params": {"text": prompt}
        }))
        await ws.recv()
        await asyncio.sleep(0.4)

        # 3. Dispatch Hardware Enter key
        await ws.send(json.dumps({
            "id": 3,
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
            "id": 4,
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

        # 4. Poll for streaming completion
        extracted_text = ""
        final_url = ""

        for poll_idx in range(timeout_seconds // 2):
            await asyncio.sleep(2)
            poll_script = """
            (() => {
                const body = document.body ? document.body.innerText : '';
                const stopBtn = document.querySelector('button[aria-label*="Stop"], button[aria-label*="Dừng"]');
                return JSON.stringify({
                    url: window.location.href,
                    bodyLength: body.length,
                    isStreaming: !!stopBtn,
                    text: body
                });
            })()
            """
            await ws.send(json.dumps({"id": 100 + poll_idx, "method": "Runtime.evaluate", "params": {"expression": poll_script}}))
            raw = await ws.recv()
            data = json.loads(json.loads(raw).get("result", {}).get("result", {}).get("value", "{}"))

            cur_url = data.get("url", "")
            is_streaming = data.get("isStreaming", False)

            if "search" in cur_url and not is_streaming and poll_idx >= 3:
                extracted_text = data.get("text", "")
                final_url = cur_url
                break

        duration = round(time.time() - start_time, 2)
        return {
            "status": "success",
            "prompt": prompt,
            "response": extracted_text,
            "search_url": final_url,
            "duration_seconds": duration,
            "quota_consumed": 0,
            "engine": "Perplexity AI (Comet Browser)",
            "substrate": "Comet CDP Port 9225"
        }


if __name__ == "__main__":
    prompt = "Third-Order Audit Gia Bao Huynh Longevity Asymmetry"
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    res = asyncio.run(query_perplexity_comet(prompt))
    print(json.dumps(res, ensure_ascii=False, indent=2))
