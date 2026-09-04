"""
LAR-OS Opera Neon Autonomous AI Bridge
Role: Zero-Quota Web AI Consultation Engine (ChatGPT, DeepSeek, Kimi) via Opera Neon Browser on CDP Port 9224
Author: Gia Bao Huynh (Jun) / Antigravity
"""

import os
import sys
import time
import json
import asyncio
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional, List
import websockets

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

CDP_PORT = 9224

AI_TARGETS = {
    "chatgpt": {
        "name": "ChatGPT (OpenAI)",
        "url": "https://chatgpt.com/",
        "login_url": "https://chatgpt.com/auth/login",
        "input_selector": "#prompt-textarea, .ProseMirror, textarea",
        "send_selector": "#composer-submit-button, button[data-testid='send-button'], button[aria-label='Gửi câu lệnh'], button[aria-label='Gửi tin nhắn'], button[aria-label='Send message']",
        "stop_selector": "button[aria-label*='Dừng'], button[aria-label*='Stop'], button[data-testid='stop-button']",
        "response_selector": "article, div[data-message-author-role='assistant'], div.agent-turn, div.markdown"
    },
    "deepseek": {
        "name": "DeepSeek-R1 / V3",
        "url": "https://chat.deepseek.com/",
        "login_url": "https://chat.deepseek.com/sign_in",
        "input_selector": "#chat-input, textarea, div[contenteditable='true']",
        "send_selector": "div[role='button']:has(svg), button[type='submit'], button[aria-label='Send']",
        "stop_selector": ".ds-icon-stop, [aria-label='stop']",
        "response_selector": ".ds-markdown, .chat-message"
    },
    "kimi": {
        "name": "Moonshot Kimi",
        "url": "https://www.kimi.com/",
        "login_url": "https://www.kimi.com/",
        "input_selector": "div[contenteditable='true'], textarea",
        "send_selector": "button[type='submit'], .send-button",
        "stop_selector": ".stop-button",
        "response_selector": ".chat-message-item-content, .markdown"
    }
}

class OperaNeonBridge:
    def __init__(self, port: int = CDP_PORT):
        self.port = port
        self.base_url = f"http://localhost:{port}"

    def is_alive(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.base_url}/json/version")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def list_tabs(self) -> List[Dict[str, Any]]:
        try:
            req = urllib.request.Request(f"{self.base_url}/json/list")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[-] Error listing tabs: {e}")
            return []

    def get_or_create_tab(self, target_domain: str, initial_url: str):
        tabs = self.list_tabs()
        # Extract primary domain keyword (e.g. 'deepseek' from 'chat.deepseek.com', 'kimi' from 'www.kimi.com')
        clean_parts = [p for p in target_domain.split(".") if p]
        if len(clean_parts) >= 3 and clean_parts[-2] in ("co", "com", "net", "org", "edu", "gov") and clean_parts[-1] in ("vn", "uk", "jp", "au"):
            keyword = clean_parts[-3].lower()
        elif len(clean_parts) >= 2:
            keyword = clean_parts[-2].lower()
        else:
            keyword = target_domain.lower()
            
        matching = [
            t for t in tabs 
            if t.get("type") == "page" and (
                target_domain in t.get("url", "") or 
                keyword in urllib.parse.urlparse(t.get("url", "")).netloc.lower()
            )
        ]
        if matching:
            return matching[0]
        # Create new tab using PUT method
        try:
            create_url = f"{self.base_url}/json/new?{urllib.parse.quote(initial_url, safe=':/?=')}"
            req = urllib.request.Request(create_url, method="PUT")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[-] Error creating tab: {e}")
            return tabs[0] if tabs else None

    async def execute_cdp(self, ws_url: str, method: str, params: Dict[str, Any] = None, timeout: float = 8.0) -> Dict[str, Any]:
        if params is None:
            params = {}
        msg_id = int(time.time() * 1000) % 1000000
        async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
            msg = {"id": msg_id, "method": method, "params": params}
            await ws.send(json.dumps(msg))
            start = time.time()
            while time.time() - start < timeout:
                try:
                    res_raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
                    res = json.loads(res_raw)
                    if res.get("id") == msg_id:
                        return res
                except (asyncio.TimeoutError, Exception):
                    break
            return {}

    async def evaluate_js(self, ws_url: str, expression: str) -> Any:
        res = await self.execute_cdp(ws_url, "Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        return res.get("result", {}).get("result", {}).get("value")

    async def inspect_target_status(self, engine: str = "chatgpt") -> Dict[str, Any]:
        cfg = AI_TARGETS.get(engine, AI_TARGETS["chatgpt"])
        domain = urllib.parse.urlparse(cfg["url"]).netloc
        tab = self.get_or_create_tab(domain, cfg["url"])
        if not tab:
            return {"status": "error", "message": f"Opera Neon tab for {engine} unavailable"}
            
        ws_url = tab["webSocketDebuggerUrl"]
        js_probe = f"""
        (function() {{
            var url = window.location.href;
            var title = document.title;
            var bodyText = document.body ? document.body.innerText : '';
            var hasCloudflare = Boolean(document.querySelector('#challenge-stage, #cf-spinner-please-wait, iframe[src*="challenges.cloudflare.com"]'));
            var inputEl = document.querySelector("{cfg['input_selector']}");
            var isAuthPage = url.includes('/auth') || url.includes('/login') || url.includes('sign_in');
            var buttons = Array.from(document.querySelectorAll('button, a')).map(b => b.innerText.trim()).filter(Boolean);
            var hasGoogleBtn = buttons.some(b => b.toLowerCase().includes('google') || b.toLowerCase().includes('tiếp tục với google'));
            
            return JSON.stringify({{
                engine: "{engine}",
                title: title,
                url: url,
                has_cloudflare_turnstile: hasCloudflare,
                has_input_area: Boolean(inputEl),
                is_auth_page: isAuthPage,
                has_google_login_btn: hasGoogleBtn,
                button_sample: buttons.slice(0, 8),
                snippet: bodyText.slice(0, 300)
            }});
        }})()
        """
        val = await self.evaluate_js(ws_url, js_probe)
        try:
            return json.loads(val)
        except Exception:
            return {"raw": val}

    async def consult_ai(self, engine: str, prompt: str, timeout_seconds: int = 45) -> Dict[str, Any]:
        cfg = AI_TARGETS.get(engine, AI_TARGETS["chatgpt"])
        domain = urllib.parse.urlparse(cfg["url"]).netloc
        tab = self.get_or_create_tab(domain, cfg["url"])
        if not tab:
            return {"status": "error", "message": f"Could not find or open {engine} in Opera Neon"}
            
        ws_url = tab["webSocketDebuggerUrl"]
        
        # Check status before sending
        status = await self.inspect_target_status(engine)
        if status.get("has_cloudflare_turnstile"):
            return {
                "status": "HUMAN_INTERVENTION_REQUIRED",
                "engine": engine,
                "reason": "Cloudflare Turnstile verification detected.",
                "action": "Please complete the verification in Opera Neon or via Chrome Remote Desktop."
            }
            
        # Navigate if not on target URL
        if domain not in tab.get("url", ""):
            await self.execute_cdp(ws_url, "Page.navigate", {"url": cfg["url"]})
            await asyncio.sleep(4)
            
        # Inject prompt using native property setter to bypass React 18 synthetic wrapper
        escaped_prompt = json.dumps(prompt)
        inject_js = f"""
        (async function() {{
            var input = document.querySelector("{cfg['input_selector']}");
            if (!input) return {{ ok: false, error: "Input selector not found" }};
            
            input.focus();
            if (input.getAttribute('contenteditable') === 'true' || input.classList.contains('ProseMirror')) {{
                document.execCommand('selectAll', false, null);
                document.execCommand('insertText', false, {escaped_prompt});
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }} else if (input.tagName === 'TEXTAREA') {{
                var setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                setter.call(input, {escaped_prompt});
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }} else if (input.tagName === 'INPUT') {{
                var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                setter.call(input, {escaped_prompt});
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }} else {{
                input.innerText = {escaped_prompt};
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            
            // Poll for send button to become enabled
            for (var i = 0; i < 12; i++) {{
                await new Promise(r => setTimeout(r, 100));
                var sendBtn = document.querySelector('#composer-submit-button') || 
                              document.querySelector('button[data-testid="send-button"]') || 
                              document.querySelector("{cfg['send_selector']}");
                if (sendBtn && !sendBtn.disabled && sendBtn.getAttribute('aria-disabled') !== 'true') {{
                    sendBtn.click();
                    return {{ ok: true, method: "button_click", tries: i }};
                }}
            }}
            
            var enterEvent = new KeyboardEvent('keydown', {{
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13,
                bubbles: true,
                cancelable: true
            }});
            input.dispatchEvent(enterEvent);
            return {{ ok: true, method: "enter_key" }};
        }})()
        """
        # Record baseline message count before injecting
        baseline_js = f"""
        (function() {{
            var els = document.querySelectorAll("{cfg['response_selector']}");
            return els.length;
        }})()
        """
        baseline_count = (await self.evaluate_js(ws_url, baseline_js)) or 0

        inject_res = await self.evaluate_js(ws_url, inject_js)
        print(f"[+] Prompt injected into {engine} (baseline {baseline_count}): {inject_res}")
        
        # Poll for response completion
        print(f"[+] Waiting for {engine} response (up to {timeout_seconds}s)...")
        start_time = time.time()
        last_text = ""
        stable_count = 0
        has_streamed = False
        
        while time.time() - start_time < timeout_seconds:
            await asyncio.sleep(2)
            scrape_js = f"""
            (function() {{
                var stopBtn = document.querySelector("{cfg['stop_selector']}");
                var responseEls = document.querySelectorAll("{cfg['response_selector']}");
                var lastEl = responseEls.length > 0 ? responseEls[responseEls.length - 1] : null;
                return JSON.stringify({{
                    is_streaming: Boolean(stopBtn),
                    text: lastEl ? lastEl.innerText.trim() : "",
                    count: responseEls.length
                }});
            }})()
            """
            scrape_val = await self.evaluate_js(ws_url, scrape_js)
            try:
                data = json.loads(scrape_val)
                current_text = data.get("text", "")
                is_streaming = data.get("is_streaming", False)
                el_count = data.get("count", 0)
                
                if is_streaming:
                    has_streamed = True

                # Valid completion if new turn appeared and streaming stopped
                if (el_count > baseline_count or has_streamed) and current_text and current_text == last_text and not is_streaming:
                    stable_count += 1
                    if stable_count >= 2:
                        print(f"[+] Response completed ({len(current_text)} chars)!")
                        return {
                            "status": "success",
                            "engine": engine,
                            "model_name": cfg["name"],
                            "prompt": prompt,
                            "response": current_text,
                            "elapsed_seconds": round(time.time() - start_time, 2),
                            "tokens_consumed": 0  # 100% free browser harvest!
                        }
                else:
                    stable_count = 0
                    last_text = current_text
            except Exception:
                pass
                
        if last_text:
            return {
                "status": "partial_success",
                "engine": engine,
                "response": last_text,
                "elapsed_seconds": timeout_seconds,
                "warning": "Polling reached timeout limit; returning latest captured output."
            }
            
        return {
            "status": "pending_or_modal",
            "engine": engine,
            "message": "Prompt submitted to Opera Neon; review browser window if authentication modal is visible.",
            "last_status": status
        }

_default_bridge: Optional[OperaNeonBridge] = None

def get_bridge() -> OperaNeonBridge:
    global _default_bridge
    if _default_bridge is None:
        _default_bridge = OperaNeonBridge()
    return _default_bridge

async def consult_opera_neon(engine: str = "chatgpt", prompt: str = "", timeout_seconds: int = 45) -> Dict[str, Any]:
    bridge = get_bridge()
    if not bridge.is_alive():
        return {
            "status": "error",
            "engine": engine,
            "message": "Opera Neon browser is not running on CDP port 9224. Launch opera_neon_cdp_daemon.py."
        }
    return await bridge.consult_ai(engine=engine, prompt=prompt, timeout_seconds=timeout_seconds)

if __name__ == "__main__":
    bridge = get_bridge()
    print("Opera Neon alive on 9224?", bridge.is_alive())
    async def test():
        status = await bridge.inspect_target_status("chatgpt")
        print("ChatGPT Status:", json.dumps(status, indent=2, ensure_ascii=False))
    asyncio.run(test())
