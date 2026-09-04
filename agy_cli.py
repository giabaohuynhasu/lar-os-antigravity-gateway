#!/usr/bin/env python3
"""
⚡ Antigravity CLI (agy) - The Universal Command-Line AI Research Operator
Integrates LAR-OS AI Gateway (5-Pro Quota Pool), Opera Neon CDP (Claude Sonnet 5, ChatGPT, Gmail),
and Google Drive Gemini Spark Hub.

Author: Gia Bao Huynh (Jun) / Antigravity
"""

import os
import sys
import json
import time
import argparse
import asyncio
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

GATEWAY_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(GATEWAY_DIR))

from gemini_spark_bridge import GeminiSparkBridge
from gmail_spark_sender import GmailSparkSender

GATEWAY_URL = "http://127.0.0.1:18797"
RECIPIENT_EMAIL = "thuaquan228@gmail.com"

# Terminal Color Codes
class Colors:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

def print_banner():
    banner = rf"""{Colors.CYAN}{Colors.BOLD}
   ___          __   _                       _   __        
  / _ | ___  __/ /_ (_)__  ________ __  __  (_) / /  __ __ 
 / __ |/ _ \/ _  // // _ \/ __/ _  /\ \/ / / / / /__/ // / 
/_/ |_/_//_/\_,_//_//_//_/_/  \_,_/  \__/ /_/ /____/\_, /  
                                                   /___/   
{Colors.BLUE}⚡ Google Antigravity CLI v3.5 (Agentic Hybrid Edition){Colors.RESET}
{Colors.DIM}User: thuaquan228@gmail.com (Gia Bao Huynh) | Gateway: {GATEWAY_URL}{Colors.RESET}
"""
    print(banner)

def check_gateway_health() -> Dict[str, Any]:
    try:
        req = urllib.request.Request(f"{GATEWAY_URL}/health")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e)}

def check_opera_neon_health() -> Dict[str, Any]:
    try:
        req = urllib.request.Request("http://localhost:9224/json")
        with urllib.request.urlopen(req, timeout=3) as resp:
            tabs = json.loads(resp.read().decode("utf-8"))
            pages = [t for t in tabs if t.get("type") == "page"]
            return {
                "status": "ONLINE",
                "tab_count": len(pages),
                "has_claude": any("claude.ai" in t.get("url", "") for t in pages),
                "has_chatgpt": any("chatgpt.com" in t.get("url", "") for t in pages),
                "has_gmail": any("mail.google.com" in t.get("url", "") for t in pages),
            }
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e)}

def show_status():
    print_banner()
    print(f"{Colors.BOLD}=== HỆ THỐNG TRẠNG THÁI ANTIGRAVITY ==={Colors.RESET}\n")
    
    # 1. Gateway Status
    gw = check_gateway_health()
    gw_color = Colors.GREEN if gw.get("status") == "ONLINE" else Colors.RED
    print(f"[{gw_color}●{Colors.RESET}] {Colors.BOLD}LAR-OS Gateway (18797):{Colors.RESET} {gw.get('status')}")
    if gw.get("status") == "ONLINE":
        pool = gw.get("pro_key_pool", {})
        print(f"    - Quota Mode: {gw.get('mode', '5-Pro Pool')}")
        print(f"    - Active Google Pro Nodes: {pool.get('active_keys', 5)} tài khoản")
    
    # 2. Opera Neon CDP Status
    neon = check_opera_neon_health()
    neon_color = Colors.GREEN if neon.get("status") == "ONLINE" else Colors.RED
    print(f"\n[{neon_color}●{Colors.RESET}] {Colors.BOLD}Opera Neon CDP (9224):{Colors.RESET} {neon.get('status')}")
    if neon.get("status") == "ONLINE":
        c_status = f"{Colors.GREEN}READY{Colors.RESET}" if neon.get("has_claude") else f"{Colors.YELLOW}NOT OPEN{Colors.RESET}"
        g_status = f"{Colors.GREEN}READY{Colors.RESET}" if neon.get("has_chatgpt") else f"{Colors.YELLOW}NOT OPEN{Colors.RESET}"
        m_status = f"{Colors.GREEN}AUTHENTICATED{Colors.RESET}" if neon.get("has_gmail") else f"{Colors.YELLOW}NOT OPEN{Colors.RESET}"
        print(f"    - Claude Sonnet 5 Max: {c_status}")
        print(f"    - ChatGPT GPT-5.6:      {g_status}")
        print(f"    - Gmail Dispatcher:     {m_status}")

    # 3. Google Drive Sync Status
    bridge = GeminiSparkBridge()
    b_stat = bridge.get_status()
    print(f"\n[{Colors.GREEN}●{Colors.RESET}] {Colors.BOLD}Google Drive Gemini Spark Hub:{Colors.RESET}")
    print(f"    - Mount Point: {bridge.bridge_dir}")
    print(f"    - Bridge State: {b_stat.get('state', 'IDLE')}")
    print(f"    - Target Mailbox: {RECIPIENT_EMAIL}")

    print("\n" + "="*50 + "\n")

async def query_model(prompt: str, model: str = "gemini-3.5-flash") -> str:
    """Dispatches query to LAR-OS Gateway or Opera Neon Bridge."""
    # Special routing for Opera Neon direct browser models
    if model in ("claude", "chatgpt"):
        from opera_neon_ai_bridge import consult_opera_neon
        print(f"{Colors.DIM}[+] Calling {model.upper()} via Opera Neon CDP...{Colors.RESET}")
        res = await consult_opera_neon(engine=model, prompt=prompt)
        return res.get("response") or res.get("message") or str(res)

    # Standard Gateway routing (5-Pro Gemini pool)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Antigravity Autonomous CLI Engine for Gia Bao Huynh (Jun). "
                    "Provide authoritative, concise, deeply technical, and structured responses with Markdown."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{GATEWAY_URL}/v1/chat/completions",
        data=req_data,
        headers={"Content-Type": "application/json", "Authorization": "Bearer agy-cli-local"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Error: Không thể kết nối Gateway ({e}). Hãy kiểm tra lar_os_gateway.py]"

async def run_prompt_workflow(prompt: str, model: str, send_email: bool):
    print(f"{Colors.CYAN}{Colors.BOLD}⚡ [AGY] Executing prompt via model:{Colors.RESET} {Colors.YELLOW}{model}{Colors.RESET}")
    print(f"{Colors.DIM}Prompt: {prompt[:120]}...{Colors.RESET}\n")

    start_time = time.time()
    response = await query_model(prompt, model)
    elapsed = round(time.time() - start_time, 2)

    # Print Response
    print(f"\n{Colors.GREEN}{Colors.BOLD}=== PHẢN HỒI TỪ ANTIGRAVITY ({elapsed}s) ==={Colors.RESET}\n")
    print(response)
    print(f"\n{Colors.DIM}" + "-"*50 + f"{Colors.RESET}\n")

    # Email Dispatch if requested
    if send_email:
        print(f"{Colors.CYAN}[+] Chuẩn bị gửi báo cáo qua Gmail tới {RECIPIENT_EMAIL}...{Colors.RESET}")
        bridge = GeminiSparkBridge()
        sender = GmailSparkSender()

        subject = f"[Antigravity CLI] Báo cáo: {prompt[:45]} - {time.strftime('%H:%M %d/%m')}"
        
        # HTML formatting
        html_report = f"""
        <div style="font-family: system-ui, -apple-system, sans-serif; max-width: 680px; margin: 0 auto; background-color: #0d1117; color: #e6edf3; padding: 24px; border-radius: 12px; border: 1px solid #30363d;">
            <h2 style="color: #58a6ff; margin-top: 0;">⚡ Antigravity CLI Execution Report</h2>
            <p style="color: #8b949e; font-size: 13px;">Executed by <code>agy</code> CLI &bull; Model: <b>{model}</b> &bull; Elapsed: {elapsed}s</p>
            <div style="background-color: #161b22; padding: 14px; border-radius: 8px; margin-bottom: 18px;">
                <b style="color: #7ee787;">Lệnh thực thi:</b>
                <p style="margin: 6px 0 0 0; color: #c9d1d9; white-space: pre-wrap;">{prompt}</p>
            </div>
            <div style="background-color: #161b22; padding: 16px; border-radius: 8px;">
                <b style="color: #58a6ff;">Nội dung phản hồi:</b>
                <div style="line-height: 1.6; margin-top: 8px; white-space: pre-wrap;">{response}</div>
            </div>
        </div>
        """
        md_content = f"# {subject}\n\n**Model:** {model}\n**Prompt:** {prompt}\n\n## Response\n\n{response}\n"
        
        # Save to Drive
        saved_file = bridge.save_report(subject, md_content, html_report)
        print(f"{Colors.GREEN}[✓] Đã lưu bản sao báo cáo lên Drive: {saved_file.name}{Colors.RESET}")

        # Dispatch Email
        res = await sender.send_report_email(subject, html_report, recipient=RECIPIENT_EMAIL)
        print(f"{Colors.GREEN}[✓] Báo cáo đã gửi thành công tới Gmail: {RECIPIENT_EMAIL}!{Colors.RESET}")

async def interactive_mode(model: str, send_email: bool):
    print_banner()
    print(f"{Colors.BOLD}Chế độ hội thoại tương tác trực tiếp (Gõ 'exit' hoặc 'quit' để thoát){Colors.RESET}")
    print(f"Model: {Colors.YELLOW}{model}{Colors.RESET} | Auto-Email: {Colors.CYAN}{send_email}{Colors.RESET}\n")

    while True:
        try:
            user_input = input(f"{Colors.GREEN}agy> {Colors.RESET}").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print(f"{Colors.DIM}Tạm biệt!{Colors.RESET}")
                break
            await run_prompt_workflow(user_input, model, send_email)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

def main():
    parser = argparse.ArgumentParser(
        prog="agy",
        description="Antigravity CLI (agy) - Điều khiển AI Agentic, Quota Pooling, và Báo Cáo Tự Động.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  agy "Tóm tắt tình hình các bài tập ASU POS 110"
  agy --email "Nghiên cứu mô hình Queueing Instability và gửi báo cáo"
  agy -m claude "Kiểm tra mã nguồn và tối ưu hóa"
  agy status
  cat prompt.txt | agy --email
        """
    )

    parser.add_argument("prompt", nargs="*", help="Nội dung prompt hoặc lệnh cần Antigravity thực thi.")
    parser.add_argument("-m", "--model", default="gemini-3.5-flash", choices=["gemini-3.5-flash", "gemini-3.5-pro", "claude", "chatgpt"], help="Mô hình AI cần sử dụng (mặc định: gemini-3.5-flash qua 5-Pro Pool).")
    parser.add_argument("-e", "--email", action="store_true", help="Tự động phát gửi báo cáo chi tiết về hộp thư thuaquan228@gmail.com qua Gmail.")
    parser.add_argument("-s", "--status", action="store_true", help="Kiểm tra trạng thái toàn diện của Gateway, Opera Neon, và Drive Sync.")
    parser.add_argument("-i", "--inbox", action="store_true", help="Kiểm tra và kích hoạt ngay các lệnh đang chờ trong Gemini Spark Drive Inbox.")

    args = parser.parse_args()

    # Case 1: Status command
    if args.status:
        show_status()
        return

    # Case 2: Process Inbox command
    if args.inbox:
        print_banner()
        print(f"{Colors.CYAN}[+] Kiểm tra Gemini Spark Drive Inbox...{Colors.RESET}")
        bridge = GeminiSparkBridge()
        cmd = bridge.read_pending_command()
        if not cmd:
            print(f"{Colors.GREEN}[✓] Hộp thư Drive trống, không có lệnh tồn đọng.{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[!] Tìm thấy lệnh: {cmd['id']}{Colors.RESET}")
            asyncio.run(run_prompt_workflow(cmd["prompt"], args.model, send_email=True))
            bridge.consume_command(cmd["id"], cmd["prompt"])
        return

    # Check for stdin (piping support)
    prompt_text = " ".join(args.prompt).strip()
    if not prompt_text and not sys.stdin.isatty():
        prompt_text = sys.stdin.read().strip()

    # Case 3: Interactive mode if no prompt provided
    if not prompt_text:
        asyncio.run(interactive_mode(args.model, args.email))
        return

    # Case 4: Execute prompt
    asyncio.run(run_prompt_workflow(prompt_text, args.model, args.email))

if __name__ == "__main__":
    main()
