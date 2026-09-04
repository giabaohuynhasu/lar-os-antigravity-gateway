"""
LAR-OS Gmail Spark Dispatcher
Automates sending reports and checking incoming prompts via the authenticated Gmail session
for thuaquan228@gmail.com on Opera Neon (CDP port 9224).

Author: Gia Bao Huynh (Jun) / Antigravity
"""

import os
import sys
import json
import time
import asyncio
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, List
import websockets

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

CDP_PORT = 9224
TARGET_EMAIL = "thuaquan228@gmail.com"

class GmailSparkSender:
    def __init__(self, port: int = CDP_PORT):
        self.port = port
        self.base_url = f"http://localhost:{port}"

    def list_tabs(self) -> List[Dict[str, Any]]:
        try:
            req = urllib.request.Request(f"{self.base_url}/json")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[-] Error listing tabs: {e}")
            return []

    def get_or_open_gmail_tab(self) -> Optional[Dict[str, Any]]:
        tabs = self.list_tabs()
        gmail_tab = next((t for t in tabs if "mail.google.com" in t.get("url", "") and t.get("type") == "page"), None)
        if gmail_tab:
            return gmail_tab
        
        try:
            req = urllib.request.Request(f"{self.base_url}/json/new?https://mail.google.com/mail/u/0/", method="PUT")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[-] Error opening Gmail tab: {e}")
            return None

    async def execute_cdp(self, ws_url: str, method: str, params: Dict[str, Any] = None, timeout: float = 10.0) -> Dict[str, Any]:
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
                except Exception:
                    break
            return {}

    async def evaluate_js(self, ws_url: str, expression: str) -> Any:
        res = await self.execute_cdp(ws_url, "Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        return res.get("result", {}).get("result", {}).get("value")

    async def send_report_email(self, subject: str, body_html: str, recipient: str = TARGET_EMAIL) -> Dict[str, Any]:
        """Composes and sends an email via the active Gmail web session in Opera Neon."""
        tab = self.get_or_open_gmail_tab()
        if not tab or not tab.get("webSocketDebuggerUrl"):
            return {"status": "error", "message": "Could not access Gmail tab on Opera Neon (port 9224)"}

        ws_url = tab["webSocketDebuggerUrl"]

        # 1. Bring tab to front and focus
        await self.execute_cdp(ws_url, "Page.bringToFront")

        # 2. Click Compose button
        escaped_subj = json.dumps(subject)
        escaped_body = json.dumps(body_html)
        escaped_to = json.dumps(recipient)

        compose_js = f"""
        (async function() {{
            // Click Compose
            var composeBtn = document.querySelector('div[role="button"][gh="cm"], div.T-I.T-I-KE.L3, [aria-label*="Compose"], [aria-label*="Soạn thư"]');
            if (!composeBtn) return {{ ok: false, error: "Compose button not found" }};
            composeBtn.click();
            
            // Wait for composer to appear
            var toInput = null;
            for (var i = 0; i < 20; i++) {{
                await new Promise(r => setTimeout(r, 200));
                toInput = document.querySelector('input[name="to"], [aria-label*="To"], [aria-label*="Tới"], input.agP');
                if (toInput) break;
            }}
            if (!toInput) return {{ ok: false, error: "Recipient input not found" }};

            // Set Recipient
            toInput.focus();
            document.execCommand('insertText', false, {escaped_to});
            toInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            toInput.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, bubbles: true }}));
            await new Promise(r => setTimeout(r, 300));

            // Set Subject
            var subjInput = document.querySelector('input[name="subjectbox"], [aria-label*="Subject"], [aria-label*="Tiêu đề"]');
            if (subjInput) {{
                subjInput.focus();
                subjInput.value = {escaped_subj};
                subjInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}

            // Set Body (rich text or text via execCommand to comply with TrustedHTML)
            var bodyEl = document.querySelector('div[role="textbox"][aria-label*="Message Body"], div[role="textbox"][aria-label*="Nội dung thư"], div[contenteditable="true"].editable');
            if (bodyEl) {{
                bodyEl.focus();
                document.execCommand('selectAll', false, null);
                var inserted = false;
                try {{
                    inserted = document.execCommand('insertHTML', false, {escaped_body});
                }} catch(e) {{}}
                if (!inserted) {{
                    var plain = {escaped_body}.replace(/<style[^>]*>.*<\/style>/gms, '')
                                              .replace(/<[^>]+>/gm, '')
                                              .replace(/&bull;/g, '•')
                                              .replace(/&nbsp;/g, ' ')
                                              .trim();
                    document.execCommand('insertText', false, plain);
                }}
                bodyEl.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }} else {{
                return {{ ok: false, error: "Message body element not found" }};
            }}

            await new Promise(r => setTimeout(r, 500));

            // Click Send
            var sendBtn = document.querySelector('div[role="button"][data-tooltip*="Send"], [aria-label*="Send"], [aria-label*="Gửi"]');
            if (sendBtn) {{
                sendBtn.click();
                return {{ ok: true, method: "send_button_click" }};
            }}
            
            // Fallback shortcut Ctrl+Enter
            bodyEl.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, ctrlKey: true, bubbles: true }}));
            return {{ ok: true, method: "ctrl_enter_shortcut" }};
        }})()
        """

        res = await self.evaluate_js(ws_url, compose_js)
        print(f"[+] Gmail Dispatch Result: {res}")
        return res or {"status": "dispatched"}

    async def scan_spark_emails(self) -> List[Dict[str, Any]]:
        """Scans for unread emails with [SPARK-PROMPT] or [GEMINI-SPARK] in subject."""
        tab = self.get_or_open_gmail_tab()
        if not tab or not tab.get("webSocketDebuggerUrl"):
            return []

        ws_url = tab["webSocketDebuggerUrl"]
        scan_js = """
        (function() {
            var rows = Array.from(document.querySelectorAll('tr.zA'));
            var sparkEmails = [];
            for (var r of rows) {
                var isUnread = r.classList.contains('zE');
                var text = r.innerText;
                if (text.includes('[SPARK-PROMPT]') || text.includes('[GEMINI-SPARK]')) {
                    var sender = r.querySelector('.yX .yW span') ? r.querySelector('.yX .yW span').innerText : "";
                    var subject = r.querySelector('.bog span') ? r.querySelector('.bog span').innerText : "";
                    var snippet = r.querySelector('.y2') ? r.querySelector('.y2').innerText : "";
                    sparkEmails.append({
                        unread: isUnread,
                        sender: sender,
                        subject: subject,
                        snippet: snippet
                    });
                }
            }
            return JSON.stringify(sparkEmails);
        })()
        """
        raw = await self.evaluate_js(ws_url, scan_js)
        try:
            return json.loads(raw) if raw else []
        except Exception:
            return []

if __name__ == "__main__":
    sender = GmailSparkSender()
    tab = sender.get_or_open_gmail_tab()
    print("[+] Gmail Tab Found:", tab.get("title") if tab else "None")
