#!/usr/bin/env python3
"""
✨ Antigravity Vibe Interpreter (vibe_interpreter.py)
Translates zero-syntax, casual, mobile Termius inputs into structured Antigravity actions.

Features:
- No quotation marks needed (captures arbitrary argv streams).
- Accented and unaccented Vietnamese normalization (telex / unaccented / slang).
- Auto-detects status checks, inbox polls, interactive chat, model routing, and Gmail dispatch.
- Strips routing noise so models receive pure, clean instructions.
"""

import re
import sys
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")


def strip_accents(text: str) -> str:
    """Removes diacritics / accents from Vietnamese or Latin text for robust matching."""
    text = text.replace("đ", "d").replace("Đ", "d")
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()

@dataclass
class VibeResult:
    action: str  # 'status', 'inbox', 'interactive', 'query'
    prompt: str
    model: str = "gemini-3.5-flash"
    send_email: bool = False
    vibe_notes: List[str] = field(default_factory=list)

def interpret_vibe(args: List[str]) -> VibeResult:
    """
    Parses a list of argument tokens into a VibeResult.
    Handles traditional flags if present (-m, -e, -s, -i) OR 100% pure vibe slang.
    """
    if not args:
        return VibeResult(
            action="interactive",
            prompt="",
            vibe_notes=["Không có tham số -> Chuyển sang chế độ hội thoại trực tiếp (Interactive Chat)"]
        )

    # Check for traditional flags first (backward compatibility)
    manual_model: Optional[str] = None
    manual_email: bool = False
    manual_status: bool = False
    manual_inbox: bool = False
    remaining_tokens: List[str] = []

    i = 0
    while i < len(args):
        tok = args[i]
        if tok in ("-s", "--status"):
            manual_status = True
        elif tok in ("-i", "--inbox"):
            manual_inbox = True
        elif tok in ("-e", "--email"):
            manual_email = True
        elif tok in ("-m", "--model") and i + 1 < len(args):
            manual_model = args[i + 1]
            i += 1
        elif tok.startswith("--model="):
            manual_model = tok.split("=", 1)[1]
        else:
            remaining_tokens.append(tok)
        i += 1

    if manual_status:
        return VibeResult(action="status", prompt="", vibe_notes=["Cờ --status được kích hoạt"])
    if manual_inbox:
        return VibeResult(action="inbox", prompt="", vibe_notes=["Cờ --inbox được kích hoạt"])

    raw_text = " ".join(remaining_tokens).strip()
    if not raw_text:
        return VibeResult(
            action="interactive",
            prompt="",
            model=manual_model or "gemini-3.5-flash",
            send_email=manual_email,
            vibe_notes=["Không có prompt -> Chế độ tương tác"]
        )

    norm_text = strip_accents(raw_text)
    notes: List[str] = []

    # 1. Check for Status Vibe
    status_keywords = [
        "st", "status", "check he thong", "khoe ko", "khoe khong", "on ko", "on khong",
        "song ko", "song khong", "sao roi", "tinh hinh", "ping", "trang thai",
        "check he thong xem on ko", "he thong sao roi", "xem trang thai", "may moc on ko"
    ]
    # Exact match or very short query
    if norm_text in status_keywords or (len(norm_text.split()) <= 4 and any(norm_text == kw or norm_text.startswith(kw) for kw in ["st", "status", "ping", "khoe ko", "sao roi", "tinh hinh"])):
        return VibeResult(
            action="status",
            prompt=raw_text,
            vibe_notes=["Nhận diện vibe: Kiểm tra trạng thái hệ thống (Status Check)"]
        )

    # 2. Check for Inbox Vibe
    inbox_keywords = [
        "ib", "inbox", "hop thu", "hop thu drive", "drive inbox", "co gi moi",
        "lenh moi", "pending", "check inbox", "check hop thu", "kiem tra hop thu"
    ]
    if norm_text in inbox_keywords or (len(norm_text.split()) <= 4 and any(norm_text == kw for kw in ["ib", "inbox", "hop thu", "co gi moi"])):
        return VibeResult(
            action="inbox",
            prompt=raw_text,
            vibe_notes=["Nhận diện vibe: Quét lệnh mới trong hộp thư Drive Inbox"]
        )

    # 3. Check for Interactive Chat Vibe
    chat_keywords = ["chat", "talk", "tro chuyen", "hoi dap", "tam su", "interactive"]
    if norm_text in chat_keywords:
        return VibeResult(
            action="interactive",
            prompt="",
            model=manual_model or "gemini-3.5-flash",
            send_email=manual_email,
            vibe_notes=["Nhận diện vibe: Bắt đầu phiên chat trực tiếp"]
        )

    # 4. Extract Model Routing from Vibe
    selected_model = manual_model or "gemini-3.5-flash"
    working_text = raw_text

    # Model routing heuristics (prefix-based or token-based)
    first_token_norm = strip_accents(remaining_tokens[0]).lower() if remaining_tokens else ""
    first_two_norm = " ".join([strip_accents(t) for t in remaining_tokens[:2]]).lower() if len(remaining_tokens) >= 2 else ""

    # Priority 1: Prefix match (e.g. `a claude <prompt>`, `vibe gpt <prompt>`)
    if first_token_norm in ("claude", "sonnet", "anthropic") or first_two_norm.startswith("claude"):
        selected_model = "claude"
        notes.append("Định tuyến sang Claude Sonnet 5 Max (qua Opera Neon CDP)")
        # Strip prefix
        working_text = re.sub(r"^(claude|sonnet|anthropic)\s*[:,-]?\s*", "", working_text, flags=re.IGNORECASE).strip()
    elif first_token_norm in ("chatgpt", "gpt", "gpt5", "gpt4", "openai") or first_two_norm in ("chat gpt", "gpt 5"):
        selected_model = "chatgpt"
        notes.append("Định tuyến sang ChatGPT GPT-5.6 (qua Opera Neon CDP)")
        working_text = re.sub(r"^(chatgpt|chat gpt|gpt5|gpt 5|gpt|openai)\s*[:,-]?\s*", "", working_text, flags=re.IGNORECASE).strip()
    elif first_token_norm in ("pro", "gemini-pro") or first_two_norm in ("gemini pro", "3.5 pro"):
        selected_model = "gemini-3.5-pro"
        notes.append("Định tuyến sang Gemini 3.5 Pro (Deep Research / Coding)")
        working_text = re.sub(r"^(pro|gemini pro|gemini-pro|3\.5 pro)\s*[:,-]?\s*", "", working_text, flags=re.IGNORECASE).strip()
    elif first_token_norm in ("flash", "gemini-flash") or first_two_norm in ("gemini flash", "3.5 flash"):
        selected_model = "gemini-3.5-flash"
        notes.append("Định tuyến sang Gemini 3.5 Flash (5-Pro Key Quota Pool)")
        working_text = re.sub(r"^(flash|gemini flash|gemini-flash|3\.5 flash)\s*[:,-]?\s*", "", working_text, flags=re.IGNORECASE).strip()
    else:
        # Check if model is mentioned anywhere with explicit directive (e.g., "hoi claude xem...", "dung gpt viet...")
        if re.search(r"\b(hoi claude|dung claude|qua claude|claude oi)\b", norm_text):
            selected_model = "claude"
            notes.append("Nhận diện từ khóa 'claude' -> Định tuyến sang Claude Sonnet 5")
        elif re.search(r"\b(hoi gpt|hoi chatgpt|dung gpt|dung chatgpt|chatgpt oi|gpt oi)\b", norm_text):
            selected_model = "chatgpt"
            notes.append("Nhận diện từ khóa 'chatgpt/gpt' -> Định tuyến sang ChatGPT")
        elif re.search(r"\b(dung pro|dung gemini pro|deep research|can pro)\b", norm_text):
            selected_model = "gemini-3.5-pro"
            notes.append("Nhận diện từ khóa 'pro' -> Định tuyến sang Gemini 3.5 Pro")
        else:
            notes.append("Mô hình mặc định: Gemini 3.5 Flash (Tốc độ cao qua 5-Pro Quota Pool)")

    # 5. Extract Email Dispatch Intent
    send_email = manual_email
    email_patterns = [
        r"(gui|send|chuyen|phat)\s+(qua\s+)?(mail|gmail|email|thu)",
        r"mail\s+(cho\s+)?(tui|toi|tao|em|anh|me)",
        r"email\s+(cho\s+)?(tui|toi|tao|em|anh|me)",
        r"(bao cao|report)\s+(qua\s+)?(mail|gmail|email)",
        r"gui\s+vao\s+(mail|gmail|email|hop thu)",
        r"nhan\s+qua\s+(mail|gmail|email)"
    ]

    working_norm = strip_accents(working_text)
    matched_email = False
    for pat in email_patterns:
        if re.search(pat, working_norm):
            matched_email = True
            break

    if matched_email:
        send_email = True
        notes.append("Nhận diện ý định gửi email -> Tự động phát báo cáo tới thuaquan228@gmail.com")
        # Clean email phrase from end of prompt to avoid confusing the LLM
        clean_prompt = re.sub(
            r"\s*(roi|kem|dong thoi)?\s*(gui|send|chuyen)?\s*(qua\s+)?(mail|gmail|email|thu)(\s+(cho\s+)?(tui|toi|tao|em|anh|me))?[\.!]?$",
            "",
            working_text,
            flags=re.IGNORECASE
        ).strip()
        if clean_prompt:
            working_text = clean_prompt

    return VibeResult(
        action="query",
        prompt=working_text if working_text else raw_text,
        model=selected_model,
        send_email=send_email,
        vibe_notes=notes
    )

if __name__ == "__main__":
    test_cases = [
        ["st"],
        ["khoe", "ko"],
        ["check", "he", "thong", "xem", "on", "ko"],
        ["ib"],
        ["co", "gi", "moi"],
        ["claude", "viet", "ham", "kiem", "tra", "so", "dien", "thoai"],
        ["gpt", "giai", "thich", "co", "che", "proof", "of", "stake"],
        ["pro", "phan", "tich", "thuat", "toan", "dijkstra"],
        ["tom", "tat", "asu", "pos", "110", "roi", "gui", "mail", "cho", "tui"],
        ["claude", "viet", "bao", "cao", "thi", "truong", "gui", "gmail"],
        ["giai", "thich", "ve", "antigravity"],
        ["-m", "claude", "-e", "kiem", "tra", "he", "thong"]
    ]

    print("=== TESTING VIBE INTERPRETER ===")
    for tc in test_cases:
        res = interpret_vibe(tc)
        print(f"\n[INPUT]: {' '.join(tc)}")
        print(f"  -> Action: {res.action}")
        print(f"  -> Model: {res.model}")
        print(f"  -> Email: {res.send_email}")
        print(f"  -> Prompt: {res.prompt}")
        print(f"  -> Notes: {', '.join(res.vibe_notes)}")
