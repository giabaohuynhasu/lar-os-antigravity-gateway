"""
LAR-OS Gemini Spark Autonomous Bridge Daemon
Listens for commands issued from Gemini Spark (Google Drive / Google Docs / Gmail)
for thuaquan228@gmail.com, processes tasks through LAR-OS AI Gateway,
and dispatches comprehensive analytical reports to thuaquan228@gmail.com via Gmail.

Author: Gia Bao Huynh (Jun) / Antigravity
"""

import os
import sys
import json
import time
import asyncio
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

from gemini_spark_bridge import GeminiSparkBridge
from gmail_spark_sender import GmailSparkSender

GATEWAY_API_URL = "http://127.0.0.1:18797/v1/chat/completions"

class GeminiSparkDaemon:
    def __init__(self, check_interval_seconds: int = 5):
        self.bridge = GeminiSparkBridge()
        self.sender = GmailSparkSender()
        self.check_interval = check_interval_seconds
        self.running = False

    async def call_gateway_ai(self, prompt: str) -> str:
        """Invokes LAR-OS AI Gateway (5-Pro Gemini Pool with Claude/GPT fallbacks)."""
        payload = {
            "model": "gemini-3.5-flash",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Antigravity Autonomous Research Assistant for Gia Bao Huynh (Jun). "
                        "The user contacted you via Gemini Spark (Google Workspace). "
                        "Formulate a structured, authoritative, and elegant response with markdown formatting, "
                        "clear executive summary, bulleted points, and actionable next steps."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            GATEWAY_API_URL,
            data=req_data,
            headers={"Content-Type": "application/json", "Authorization": "Bearer lar-os-spark-key"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Error contacting LAR-OS Gateway: {e}. Output generated locally.]"

    def format_html_report(self, title: str, prompt: str, ai_response: str) -> str:
        """Formats the response into a sleek, professional HTML email report."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 680px; margin: 0 auto; background-color: #0d1117; color: #e6edf3; padding: 24px; border-radius: 12px; border: 1px solid #30363d;">
            <div style="border-bottom: 2px solid #58a6ff; padding-bottom: 12px; margin-bottom: 20px;">
                <h2 style="color: #58a6ff; margin: 0; font-size: 20px;">⚡ Antigravity x Gemini Spark Report</h2>
                <p style="color: #8b949e; margin: 4px 0 0 0; font-size: 13px;">Channel: Gemini Spark &bull; Time: {timestamp} &bull; Account: thuaquan228@gmail.com</p>
            </div>

            <div style="background-color: #161b22; padding: 16px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 20px;">
                <h4 style="color: #7ee787; margin: 0 0 8px 0; font-size: 14px; text-transform: uppercase;">📩 Prompt Nhận Từ Gemini Spark</h4>
                <p style="margin: 0; color: #c9d1d9; font-style: italic; white-space: pre-wrap;">{prompt}</p>
            </div>

            <div style="background-color: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 20px;">
                <h4 style="color: #58a6ff; margin: 0 0 12px 0; font-size: 14px; text-transform: uppercase;">📊 Phản Hồi & Báo Cáo Chi Tiết</h4>
                <div style="line-height: 1.6; color: #e6edf3; font-size: 14px; white-space: pre-wrap;">{ai_response}</div>
            </div>

            <div style="border-top: 1px solid #30363d; padding-top: 12px; font-size: 12px; color: #8b949e; text-align: center;">
                <p style="margin: 0;">Cổng giao tiếp tự động Antigravity IDE &bull; Quản trị bởi LAR-OS Gateway &bull; Đồng bộ thời gian thực qua Google Drive</p>
            </div>
        </div>
        """
        return html

    async def process_command(self, cmd: Dict[str, Any]):
        prompt = cmd["prompt"]
        cmd_id = cmd["id"]
        source = cmd.get("source", "gemini_spark")
        print(f"\n[⚡] Processing Spark Command [{cmd_id}] from {source}...")

        # 1. Update status to PROCESSING
        self.bridge.update_status(
            "PROCESSING",
            command_id=cmd_id,
            prompt=prompt[:150],
            source=source
        )

        # 2. Query AI Gateway
        response = await self.call_gateway_ai(prompt)

        # 3. Format Report & Save to Drive
        subject = f"[Antigravity Report] Phản hồi yêu cầu từ Gemini Spark - {time.strftime('%H:%M %d/%m')}"
        html_report = self.format_html_report(subject, prompt, response)
        md_content = f"# {subject}\n\n**Prompt:** {prompt}\n\n## Response\n\n{response}\n"
        report_path = self.bridge.save_report(subject, md_content, html_report)
        print(f"[✓] Report archived to Drive: {report_path.name}")

        # 4. Dispatch Email via Gmail Opera Neon CDP
        try:
            email_res = await self.sender.send_report_email(subject, html_report)
            print(f"[✓] Email dispatched to thuaquan228@gmail.com: {email_res}")
        except Exception as e:
            print(f"[!] Email dispatch error: {e}")

        # 5. Archive command and set status to COMPLETED
        self.bridge.consume_command(cmd_id, prompt)
        self.bridge.update_status(
            "COMPLETED",
            command_id=cmd_id,
            completed_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            report_file=report_path.name
        )
        print(f"[✓] Task {cmd_id} fully completed!")

    async def run_once(self) -> bool:
        """Checks for new commands and processes if found. Returns True if a command was handled."""
        cmd = self.bridge.read_pending_command()
        if cmd:
            await self.process_command(cmd)
            return True
        return False

    async def start(self):
        """Continuous polling loop."""
        self.running = True
        print(f"[+] Gemini Spark Daemon running (polling every {self.check_interval}s)...")
        print(f"[+] Listening at: {self.bridge.inbox_file}")
        while self.running:
            try:
                await self.run_once()
            except Exception as e:
                print(f"[-] Daemon loop error: {e}")
            await asyncio.sleep(self.check_interval)

if __name__ == "__main__":
    daemon = GeminiSparkDaemon(check_interval_seconds=4)
    asyncio.run(daemon.start())
