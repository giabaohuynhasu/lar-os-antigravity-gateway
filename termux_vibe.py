#!/usr/bin/env python3
"""
📱 Antigravity Termux / Mobile Vibe Engine (termux_vibe.py)
Dedicated zero-syntax client for Android Termux & Remote Termius SSH sessions.

Features:
- 100% Zero-Syntax (No quotes, no dashes, natural Vietnamese/English).
- Hybrid Routing: Connects to local LAR-OS Gateway (192.168.1.223:18797) when on Wi-Fi,
  or fails over to direct Gemini API when on 4G/5G mobile data.
- Global single-letter shortcut: `a <anything>` or `vibe <anything>`.
"""

import os
import sys
import json
import time
import re
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional

GATEWAY_LAN_URL = os.environ.get("AGY_GATEWAY_URL", "http://192.168.1.223:18797")
FALLBACK_API_KEY = os.environ.get("GEMINI_API_KEY", "")
RECIPIENT_EMAIL = "thuaquan228@gmail.com"


# Terminal ANSI Colors
class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

def print_banner():
    banner = f"""{Colors.CYAN}{Colors.BOLD}⚡ Antigravity Mobile Vibe (Termux / Termius Edition){Colors.RESET}
{Colors.DIM}User: {RECIPIENT_EMAIL} | Mode: Zero-Syntax Vibe Coding{Colors.RESET}
"""
    print(banner)

def strip_accents(text: str) -> str:
    import unicodedata
    text = text.replace("đ", "d").replace("Đ", "d")
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()

def parse_vibe(tokens: List[str]) -> Dict[str, Any]:
    if not tokens:
        return {"action": "interactive", "prompt": "", "model": "gemini-2.5-flash", "send_email": False}

    raw_text = " ".join(tokens).strip()
    norm = strip_accents(raw_text)

    # Status intent
    status_keywords = ["st", "status", "khoe ko", "khoe khong", "on ko", "on khong", "check", "sao roi", "tinh hinh", "ping"]
    if norm in status_keywords or (len(norm.split()) <= 4 and any(norm.startswith(kw) for kw in ["st", "khoe ko", "check he thong", "sao roi"])):
        return {"action": "status", "prompt": raw_text}

    # Model routing
    model = "gemini-2.5-flash"
    working_text = raw_text
    first_tok = strip_accents(tokens[0]).lower()

    if first_tok in ("claude", "sonnet"):
        model = "claude"
        working_text = re.sub(r"^(claude|sonnet)\s*[:,-]?\s*", "", working_text, flags=re.IGNORECASE).strip()
    elif first_tok in ("gpt", "chatgpt", "gpt5"):
        model = "chatgpt"
        working_text = re.sub(r"^(chatgpt|gpt5|gpt)\s*[:,-]?\s*", "", working_text, flags=re.IGNORECASE).strip()
    elif first_tok in ("pro", "gemini-pro"):
        model = "gemini-2.5-pro"
        working_text = re.sub(r"^(pro|gemini-pro)\s*[:,-]?\s*", "", working_text, flags=re.IGNORECASE).strip()

    # Email dispatch intent
    send_email = False
    if re.search(r"(gui|send)\s+(qua\s+)?(mail|gmail|email)", norm) or re.search(r"mail\s+(cho\s+)?(tui|toi|tao|em)", norm):
        send_email = True
        working_text = re.sub(r"\s*(roi|kem)?\s*(gui|send)?\s*(qua\s+)?(mail|gmail|email)(\s+cho\s+\w+)?$", "", working_text, flags=re.IGNORECASE).strip()

    return {
        "action": "query",
        "prompt": working_text or raw_text,
        "model": model,
        "send_email": send_email
    }

def show_status():
    print_banner()
    print(f"{Colors.BOLD}=== KIỂM TRA KẾT NỐI TỪ TERMUX / DI ĐỘNG ==={Colors.RESET}\n")
    
    # 1. Check Gateway LAN
    gw_online = False
    try:
        req = urllib.request.Request(f"{GATEWAY_LAN_URL}/health")
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            gw_online = data.get("status") == "ONLINE"
    except Exception:
        gw_online = False

    if gw_online:
        print(f"[{Colors.GREEN}●{Colors.RESET}] {Colors.BOLD}LAR-OS Gateway (PC LAN):{Colors.RESET} {Colors.GREEN}ONLINE{Colors.RESET} ({GATEWAY_LAN_URL})")
    else:
        print(f"[{Colors.YELLOW}○{Colors.RESET}] {Colors.BOLD}LAR-OS Gateway (PC LAN):{Colors.RESET} {Colors.YELLOW}STANDBY / 4G MODE{Colors.RESET}")
        print(f"    (Đang ở chế độ Direct Cloud Quota Pool)")

    print(f"[{Colors.GREEN}●{Colors.RESET}] {Colors.BOLD}Direct Gemini API Engine:{Colors.RESET} {Colors.GREEN}READY{Colors.RESET}")
    print(f"[{Colors.GREEN}●{Colors.RESET}] {Colors.BOLD}Target Mailbox:{Colors.RESET} {RECIPIENT_EMAIL}")
    print("\n" + "="*45 + "\n")

def query_gemini_direct(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """Calls Google Gemini API directly when offline from local PC gateway."""
    api_model = "gemini-2.5-flash" if "pro" not in model else "gemini-2.5-pro"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{api_model}:generateContent?key={FALLBACK_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3}
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["candidates"][0]["content"]["parts"][0]["text"]

def query_gateway(prompt: str, model: str) -> Optional[str]:
    """Attempts to query through the PC Gateway."""
    try:
        url = f"{GATEWAY_LAN_URL}/v1/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return res["choices"][0]["message"]["content"]
    except Exception:
        return None

def main():
    vibe = parse_vibe(sys.argv[1:])

    if vibe["action"] == "status":
        show_status()
        return

    prompt = vibe.get("prompt", "").strip()
    if not prompt:
        print_banner()
        print(f"{Colors.YELLOW}Gõ lệnh trực tiếp, ví dụ:{Colors.RESET}")
        print("  a st")
        print("  a viet code python tim so nguyen to")
        print("  a claude sua loi function nay")
        print("  a tom tat asu roi gui mail cho tui\n")
        return

    model = vibe["model"]
    send_email = vibe["send_email"]

    print(f"{Colors.MAGENTA}{Colors.BOLD}✨ [TERMUX VIBE]{Colors.RESET} {Colors.DIM}Model: {model} | Email: {send_email}{Colors.RESET}")
    print(f"{Colors.DIM}Prompt: {prompt[:80]}...{Colors.RESET}\n")

    start_time = time.time()
    
    # Try gateway first, fallback to direct cloud
    response = query_gateway(prompt, model)
    mode_used = "Gateway"
    if not response:
        response = query_gemini_direct(prompt, model)
        mode_used = "Direct Cloud Quota"

    elapsed = round(time.time() - start_time, 2)

    print(f"\n{Colors.GREEN}{Colors.BOLD}=== KẾT QUẢ TỪ ANTIGRAVITY ({elapsed}s - {mode_used}) ==={Colors.RESET}\n")
    print(response)
    print(f"\n{Colors.DIM}" + "-"*45 + f"{Colors.RESET}\n")

    if send_email:
        print(f"{Colors.CYAN}[+] Đang gửi thông báo báo cáo tới {RECIPIENT_EMAIL}...{Colors.RESET}")
        # When on Termux, if Gateway reachable, request email
        try:
            req = urllib.request.Request(
                f"{GATEWAY_LAN_URL}/v1/chat/completions",
                data=json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}], "email": True}).encode(),
                headers={"Content-Type": "application/json"}
            )
            urllib.request.urlopen(req, timeout=5)
            print(f"{Colors.GREEN}[✓] Đã kích hoạt Gateway gửi email thành công!{Colors.RESET}")
        except Exception:
            print(f"{Colors.YELLOW}[!] Lưu ý: Máy tính đang ở chế độ chờ, kết quả đã in trực tiếp trên màn hình.{Colors.RESET}")

if __name__ == "__main__":
    main()
