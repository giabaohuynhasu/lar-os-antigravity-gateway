"""
LAR-OS Gemini Spark <-> Antigravity Communication Hub
Manages Google Drive real-time command intake, status tracking, and report persistence
for thuaquan228@gmail.com on Windows (Drive G:)

Author: Gia Bao Huynh (Jun) / Antigravity
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

DRIVE_G_CANDIDATES = [
    Path(r"G:\Drive của tôi"),
    Path(r"G:\My Drive"),
    Path(r"G:"),
]

def find_spark_bridge_dir() -> Path:
    for candidate in DRIVE_G_CANDIDATES:
        if candidate.exists():
            target = candidate / "Gemini_Spark_Bridge"
            target.mkdir(parents=True, exist_ok=True)
            return target
    # Fallback to local gateway folder if G: is temporarily unavailable
    fallback = Path(__file__).resolve().parent / "spark_bridge_fallback"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback

class GeminiSparkBridge:
    def __init__(self, bridge_dir: Optional[Path] = None):
        self.bridge_dir = bridge_dir or find_spark_bridge_dir()
        self.inbox_file = self.bridge_dir / "COMMAND_INBOX.md"
        self.status_file = self.bridge_dir / "STATUS.json"
        self.reports_dir = self.bridge_dir / "Reports"
        self.archive_dir = self.bridge_dir / "Archive"
        self.init_directories()

    def init_directories(self):
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.inbox_file.exists():
            header = (
                "# Gemini Spark Command Inbox\n\n"
                "<!-- USER INSTRUCTIONS: Write or dictate commands to Gemini Spark here. -->\n"
                "<!-- Gemini Spark in Google Docs or Google Drive can append tasks below. -->\n\n"
            )
            self.inbox_file.write_text(header, encoding="utf-8")

        if not self.status_file.exists():
            self.update_status("IDLE", message="Gemini Spark Bridge active and listening.")

    def update_status(self, state: str, **kwargs) -> Dict[str, Any]:
        """States: IDLE | PROCESSING | COMPLETED | ERROR"""
        data = {
            "state": state,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "bridge_dir": str(self.bridge_dir),
            "target_account": "thuaquan228@gmail.com",
            **kwargs
        }
        self.status_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return data

    def get_status(self) -> Dict[str, Any]:
        if not self.status_file.exists():
            return {"state": "UNKNOWN"}
        try:
            return json.loads(self.status_file.read_text(encoding="utf-8"))
        except Exception:
            return {"state": "CORRUPT"}

    def read_pending_command(self) -> Optional[Dict[str, Any]]:
        """Reads user command from COMMAND_INBOX.md if one exists and is not blank."""
        if not self.inbox_file.exists():
            return None

        content = self.inbox_file.read_text(encoding="utf-8").strip()
        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("<!--") and not line.startswith("#")]
        prompt_text = "\n".join(lines).strip()

        if not prompt_text:
            return None

        cmd_id = f"cmd_{int(time.time())}"
        return {
            "id": cmd_id,
            "prompt": prompt_text,
            "raw_content": content,
            "source": "google_drive_spark_inbox",
            "detected_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def consume_command(self, cmd_id: str, prompt_text: str):
        """Archives the executed command and resets COMMAND_INBOX.md to clean state."""
        # Archive
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        archive_file = self.archive_dir / f"{timestamp}_{cmd_id}.md"
        archive_file.write_text(f"# Archived Command: {cmd_id}\n\n**Executed at:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n## Content\n\n{prompt_text}\n", encoding="utf-8")

        # Reset Inbox
        header = (
            "# Gemini Spark Command Inbox\n\n"
            "<!-- USER INSTRUCTIONS: Write or dictate commands to Gemini Spark here. -->\n"
            "<!-- Gemini Spark in Google Docs or Google Drive can append tasks below. -->\n\n"
        )
        self.inbox_file.write_text(header, encoding="utf-8")

    def save_report(self, title: str, markdown_content: str, html_content: Optional[str] = None) -> Path:
        """Saves analytical report to the Reports folder on Google Drive."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        clean_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title).strip()
        if not clean_title:
            clean_title = "Antigravity_Report"
        clean_title = clean_title.replace(" ", "_")[:50]

        md_file = self.reports_dir / f"{timestamp}_{clean_title}.md"
        md_file.write_text(markdown_content, encoding="utf-8")

        if html_content:
            html_file = self.reports_dir / f"{timestamp}_{clean_title}.html"
            html_file.write_text(html_content, encoding="utf-8")

        return md_file

if __name__ == "__main__":
    bridge = GeminiSparkBridge()
    print("[+] Gemini Spark Bridge initialized at:", bridge.bridge_dir)
    print("[+] Current Status:", bridge.get_status())
