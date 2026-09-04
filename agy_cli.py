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
from vibe_interpreter import interpret_vibe, VibeResult

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

async def interactive_mode(default_model: str = "gemini-3.5-flash", default_email: bool = False):
    print_banner()
    print(f"{Colors.BOLD}✨ Chế độ Vibe Chat tương tác trực tiếp cho Termius & Terminal{Colors.RESET}")
    print(f"{Colors.DIM}Gõ tự nhiên không cần cú pháp. Nhập 'exit', 'q' để thoát. Nhập 'st' để xem trạng thái.{Colors.RESET}")
    print(f"Mô hình gốc: {Colors.YELLOW}{default_model}{Colors.RESET} | Auto-Email: {Colors.CYAN}{default_email}{Colors.RESET}\n")

    current_model = default_model
    current_email = default_email

    while True:
        try:
            user_input = input(f"{Colors.GREEN}vibe> {Colors.RESET}").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print(f"{Colors.DIM}Tạm biệt! Hẹn gặp lại trên Termius/Antigravity.{Colors.RESET}")
                break

            # Run through vibe interpreter
            vibe = interpret_vibe(user_input.split())
            if vibe.action == "status":
                show_status()
                continue
            elif vibe.action == "inbox":
                print(f"{Colors.CYAN}[+] Kiểm tra Gemini Spark Drive Inbox...{Colors.RESET}")
                bridge = GeminiSparkBridge()
                cmd = bridge.read_pending_command()
                if not cmd:
                    print(f"{Colors.GREEN}[✓] Hộp thư Drive trống, không có lệnh tồn đọng.{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}[!] Tìm thấy lệnh: {cmd['id']}{Colors.RESET}")
                    await run_prompt_workflow(cmd["prompt"], vibe.model, send_email=True)
                    bridge.consume_command(cmd["id"], cmd["prompt"])
                continue
            
            # Query action
            target_model = vibe.model if vibe.model != "gemini-3.5-flash" else current_model
            target_email = vibe.send_email or current_email

            if vibe.vibe_notes:
                print(f"{Colors.MAGENTA}✨ [VIBE]{Colors.RESET} {Colors.DIM}" + " • ".join(vibe.vibe_notes) + f"{Colors.RESET}")

            await run_prompt_workflow(vibe.prompt, target_model, target_email)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

def has_stdin_data() -> bool:
    """Checks if there is data waiting on stdin without blocking (Windows-safe)."""
    if sys.stdin is None or sys.stdin.isatty():
        return False
    if sys.platform == "win32":
        try:
            import msvcrt
            import ctypes
            from ctypes import wintypes
            handle = msvcrt.get_osfhandle(sys.stdin.fileno())
            avail = wintypes.DWORD()
            res = ctypes.windll.kernel32.PeekNamedPipe(
                wintypes.HANDLE(handle), None, 0, None, ctypes.byref(avail), None
            )
            return bool(res and avail.value > 0)
        except Exception:
            return False
    return False

def main():
    raw_args = sys.argv[1:]

    # Help flag check
    if any(h in raw_args for h in ("-h", "--help", "help")):
        parser = argparse.ArgumentParser(
            prog="agy / a / vibe",
            description="Antigravity CLI (agy / a / vibe) - Vibe Coding AI Operator cho Termius & Terminal.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Ví dụ Vibe Coding (Termius không cần ngoặc kép, không cần cờ):
  a st
  a khoe ko
  a claude sua loi sql injection giup tui
  vibe gpt giai thich co che consensus
  a tom tat asu roi gui mail cho tui
  a co gi moi
  vibe
            """
        )
        parser.add_argument("prompt", nargs="*", help="Lệnh hoặc câu hỏi cần AI xử lý.")
        parser.add_argument("-m", "--model", default="gemini-3.5-flash", choices=["gemini-3.5-flash", "gemini-3.5-pro", "claude", "chatgpt"])
        parser.add_argument("-e", "--email", action="store_true")
        parser.add_argument("-s", "--status", action="store_true")
        parser.add_argument("-i", "--inbox", action="store_true")
        parser.print_help()
        return

    # Check for stdin (piping support)
    piped_text = ""
    if has_stdin_data():
        try:
            piped_text = sys.stdin.read().strip()
        except Exception:
            pass

    # Run Vibe Interpreter
    vibe = interpret_vibe(raw_args)


    # Attach piped text if present
    if piped_text:
        if vibe.prompt:
            vibe.prompt = f"{vibe.prompt}\n\n[Dữ liệu đính kèm]:\n{piped_text}"
        else:
            vibe.prompt = piped_text
        if vibe.action in ("interactive", "status", "inbox") and piped_text:
            vibe.action = "query"

    # Action 1: Status
    if vibe.action == "status":
        show_status()
        return

    # Action 2: Inbox check
    if vibe.action == "inbox":
        print_banner()
        print(f"{Colors.CYAN}[+] Kiểm tra Gemini Spark Drive Inbox...{Colors.RESET}")
        bridge = GeminiSparkBridge()
        cmd = bridge.read_pending_command()
        if not cmd:
            print(f"{Colors.GREEN}[✓] Hộp thư Drive trống, không có lệnh tồn đọng.{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[!] Tìm thấy lệnh: {cmd['id']}{Colors.RESET}")
            asyncio.run(run_prompt_workflow(cmd["prompt"], vibe.model, send_email=True))
            bridge.consume_command(cmd["id"], cmd["prompt"])
        return

    # Action 3: Interactive mode
    if vibe.action == "interactive":
        asyncio.run(interactive_mode(vibe.model, vibe.send_email))
        return

    # Action 4: Query workflow
    if vibe.vibe_notes:
        print(f"{Colors.MAGENTA}{Colors.BOLD}✨ [VIBE INTERPRETER]{Colors.RESET} {Colors.DIM}" + " • ".join(vibe.vibe_notes) + f"{Colors.RESET}")

    asyncio.run(run_prompt_workflow(vibe.prompt, vibe.model, vibe.send_email))


if __name__ == "__main__":
    main()
