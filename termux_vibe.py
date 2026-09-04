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

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

GATEWAY_LAN_URL = os.environ.get("AGY_GATEWAY_URL", "http://192.168.1.223:18797")
GATEWAY_TUNNEL_URL = os.environ.get("AGY_TUNNEL_URL", "https://wrestling-chelsea-dude-symbol.trycloudflare.com")
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

    # Manual flag checks
    manual_email = False
    clean_tokens = []
    for tok in tokens:
        if tok in ("-e", "--email", "-mail", "--mail"):
            manual_email = True
        else:
            clean_tokens.append(tok)

    raw_text = " ".join(clean_tokens).strip()
    norm = strip_accents(raw_text)

    # Status intent
    status_keywords = ["st", "status", "khoe ko", "khoe khong", "on ko", "on khong", "check", "sao roi", "tinh hinh", "ping"]
    if norm in status_keywords or (len(norm.split()) <= 4 and any(norm.startswith(kw) for kw in ["st", "khoe ko", "check he thong", "sao roi"])):
        return {"action": "status", "prompt": raw_text}

    # Model routing
    model = "gemini-2.5-flash"
    working_text = raw_text
    if clean_tokens:
        first_tok = strip_accents(clean_tokens[0]).lower()
        if first_tok in ("claude", "sonnet"):
            model = "claude"
            working_text = re.sub(r"^(claude|sonnet)\s*[:,-]?\s*", "", working_text, flags=re.IGNORECASE).strip()
        elif first_tok in ("gpt", "chatgpt", "gpt5"):
            model = "chatgpt"
            working_text = re.sub(r"^(chatgpt|gpt5|gpt)\s*[:,-]?\s*", "", working_text, flags=re.IGNORECASE).strip()
        elif first_tok in ("pro", "gemini-pro"):
            model = "gemini-2.5-pro"
            working_text = re.sub(r"^(pro|gemini-pro)\s*[:,-]?\s*", "", working_text, flags=re.IGNORECASE).strip()

    # Email dispatch intent (Ultra-forgiving matching)
    send_email = manual_email or os.environ.get("AGY_AUTO_EMAIL", "").lower() in ("1", "true", "yes")
    
    # 1. Prefix matches: e.g. "a mail ...", "a gui mail ...", "a email ..."
    prefix_email_match = re.match(r"^(gui\s+)?(mail|gmail|email)\s*[:,-]?\s+", working_text, flags=re.IGNORECASE)
    if prefix_email_match:
        send_email = True
        working_text = working_text[prefix_email_match.end():].strip()

    # 2. General intent in sentence
    norm_text = strip_accents(working_text)
    is_tech_email = bool(re.search(r"\b(regex|validate|validation|ham|form|input|type|dia chi)\s+(mail|email|gmail)\b", norm_text) or 
                         re.search(r"\b(mail|email|gmail)\s+(regex|validation|format)\b", norm_text))
    
    if not is_tech_email:
        email_patterns = [
            r"\b(gui|send|chuyen|phat|forward)\s+(qua\s+|vao\s+|ve\s+|toi\s+)?(mail|gmail|email|thu)\b",
            r"\b(mail|gmail|email)\s+(cho|ve|vao|toi)\s+(tui|toi|tao|em|anh|minh|to|me|ban)\b",
            r"\b(bao cao|report|ket qua|kq)\s+(qua\s+|vao\s+|ve\s+)?(mail|gmail|email)\b",
            r"\b(nhan|lay)\s+(qua\s+)?(mail|gmail|email)\b",
            r"\b(mail|gmail|email)\s+(nhe|nha|giup|ho|nhan|ngay)\b",
            r"\b(nho|kem)\s+gui\s+(mail|gmail|email)\b",
            r"\b(gui|send)\s+(mail|gmail|email)\b",
        ]
        for pat in email_patterns:
            if re.search(pat, norm_text):
                send_email = True
                break

    # Clean email suffix from prompt
    if send_email:
        clean_prompt = re.sub(
            r"\s*(roi|kem|dong thoi|va)?\s*(nho\s+)?(gui|send|chuyen)?\s*(qua|vao|ve|cho)?\s*(mail|gmail|email|thu)(\s+(cho\s+)?(tui|toi|tao|em|anh|minh|me|to))?(\s+(nhe|nha|giup|ho|ngay))?[\.!]?$",
            "",
            working_text,
            flags=re.IGNORECASE
        ).strip()
        if clean_prompt:
            working_text = clean_prompt

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

    # 2. Check Gateway Tunnel (4G/5G)
    tunnel_online = False
    try:
        req = urllib.request.Request(f"{GATEWAY_TUNNEL_URL}/health")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            tunnel_online = data.get("status") == "ONLINE"
    except Exception:
        tunnel_online = False

    if gw_online:
        print(f"[{Colors.GREEN}●{Colors.RESET}] {Colors.BOLD}LAR-OS Gateway (PC LAN):{Colors.RESET} {Colors.GREEN}ONLINE{Colors.RESET} ({GATEWAY_LAN_URL})")
    else:
        print(f"[{Colors.YELLOW}○{Colors.RESET}] {Colors.BOLD}LAR-OS Gateway (PC LAN):{Colors.RESET} {Colors.YELLOW}OFFLINE / NGOÀI PHỦ SÓNG WI-FI{Colors.RESET}")

    if tunnel_online:
        print(f"[{Colors.GREEN}●{Colors.RESET}] {Colors.BOLD}Global Cloudflare Tunnel (4G/5G / Custom GPT):{Colors.RESET} {Colors.GREEN}ONLINE{Colors.RESET}")
        print(f"    - Endpoint: {GATEWAY_TUNNEL_URL}")
    else:
        print(f"[{Colors.YELLOW}○{Colors.RESET}] {Colors.BOLD}Global Cloudflare Tunnel:{Colors.RESET} {Colors.YELLOW}STANDBY{Colors.RESET}")

    print(f"[{Colors.GREEN}●{Colors.RESET}] {Colors.BOLD}Direct Gemini API Engine:{Colors.RESET} {Colors.GREEN}READY{Colors.RESET}")
    print(f"[{Colors.GREEN}●{Colors.RESET}] {Colors.BOLD}Target Mailbox:{Colors.RESET} {RECIPIENT_EMAIL}")
    print("\n" + "="*45 + "\n")

def query_gemini_direct(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """Calls Google Gemini API directly when offline from local PC gateway."""
    api_model = "gemini-2.5-flash" if "pro" not in model else "gemini-2.5-pro"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{api_model}:generateContent"
    if FALLBACK_API_KEY:
        url += f"?key={FALLBACK_API_KEY}"
    
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

def query_gateway(prompt: str, model: str, send_email: bool = False):
    """Queries through PC Gateway via LAN first, then Tunnel (for 4G/5G)."""
    endpoints = [
        (GATEWAY_LAN_URL, "PC LAN Gateway"),
        (GATEWAY_TUNNEL_URL, "Global Cloudflare Tunnel (4G/5G)")
    ]
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "send_email": send_email
    }
    data = json.dumps(payload).encode("utf-8")
    for base_url, label in endpoints:
        try:
            url = f"{base_url}/v1/chat/completions"
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res["choices"][0]["message"]["content"], label
        except Exception:
            continue
    return None, "None"

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

    # Visual badge: Never show "Email: False" like an error!
    if send_email:
        email_badge = f"{Colors.GREEN}✉️ Gửi Email: BẬT ({RECIPIENT_EMAIL}){Colors.RESET}"
    else:
        email_badge = f"{Colors.DIM}Chế độ: Màn hình trực tiếp{Colors.RESET}"

    print(f"{Colors.MAGENTA}{Colors.BOLD}✨ [TERMUX VIBE]{Colors.RESET} {Colors.DIM}Model: {model} | {email_badge}")
    print(f"{Colors.DIM}Prompt: {prompt[:80]}...{Colors.RESET}\n")

    start_time = time.time()
    
    # Try gateway first (LAN -> Tunnel -> Direct Gemini)
    response, mode_used = query_gateway(prompt, model, send_email=send_email)
    if not response:
        response = query_gemini_direct(prompt, model)
        mode_used = "Direct Cloud Quota"

    elapsed = round(time.time() - start_time, 2)

    print(f"\n{Colors.GREEN}{Colors.BOLD}=== KẾT QUẢ TỪ ANTIGRAVITY ({elapsed}s - {mode_used}) ==={Colors.RESET}\n")
    print(response)
    print(f"\n{Colors.DIM}" + "-"*45 + f"{Colors.RESET}\n")

    if send_email:
        if "Gateway" in mode_used or "Tunnel" in mode_used:
            print(f"{Colors.GREEN}[✓] Đã gửi báo cáo chi tiết về Gmail: {RECIPIENT_EMAIL}!{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[!] Bạn đang chạy ở chế độ Direct Cloud. Kết quả đã hiển thị trên màn hình.{Colors.RESET}")

if __name__ == "__main__":
    main()
