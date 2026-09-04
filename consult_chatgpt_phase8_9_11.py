import asyncio
import sys
import json
from opera_neon_ai_bridge import get_bridge

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

PROMPT = """
Chào GPT! Báo cáo tiến độ LAR-OS Gateway:
1. Phase 3 & 4 (Adaptive Health Scoring 0->100 + Latency EMA alpha=0.2) ĐÃ HOÀN TẤT & VERIFIED.
2. Phase 5 & 6 (SQLite WAL Telemetry <2MB + Event-Driven Prune every 512 events) ĐÃ HOÀN TẤT & VERIFIED.
3. Phase 7 (Bounded Retry Budget 25s hard deadline, max 5 hops, decorrelated jitter, retry classification) ĐÃ HOÀN TẤT & VERIFIED.
4. Phase 10 (Zero-Framework Dashboard <8KB HTML/CSS/JS at /dashboard, auto-pauses when hidden) ĐÃ HOÀN TẤT & VERIFIED.
Tất cả đã đồng bộ lên GitHub, Hugging Face và Obsidian Vault. Resource footprint hiện tại: RAM ~35MB, CPU Idle 0.0%, SQLite DB 84KB.

Bây giờ nhờ GPT tư vấn chi tiết cho 3 giai đoạn còn lại:
1. Phase 8 — CLIProxy Deep Health Check:
   - Làm thế nào phân biệt Process Liveness (PID running, port 18798 listening) vs Upstream Liveness (Google OAuth token còn sống hay expired/invalid)?
   - Probing thế nào để KHÔNG spam quota, KHÔNG tốn tài nguyên và zero overhead?
2. Phase 9 — Gateway Process Self-Isolation:
   - Làm thế nào cô lập tuyệt đối các tầng (Tier-1..5 Gemini, Tier-3 Neon, Tier-4 Antigravity Go CLIProxy) để bất kỳ exception/timeout/crash ở một tầng không bao giờ làm crash gateway hay rò rỉ socket?
3. Phase 11 — Comprehensive Chaos Testing Plan:
   - Thiết kế script test độ bền tự động (Chaos Test) thuần Python/PowerShell (không Docker, không k8s):
     + Kịch bản 1: Kill ngẫu nhiên 1->5 tài khoản Gemini (giả lập 429/auth fail).
     + Kịch bản 2: Kill đột ngột process cli-proxy-api.exe giữa chừng.
     + Kịch bản 3: Giả lập rớt mạng / socket timeout.
     + Đo lường bất biến: Request client có luôn thành công qua đường dự phòng trong budget 25s không?

Nhờ GPT đưa ra kiến trúc tối ưu, code mẫu Python tinh gọn chuẩn Golden Invariant (RAM < 45MB, CPU 0%, siêu nhẹ)!
"""

async def main():
    bridge = get_bridge()
    print("Checking Opera Neon CDP on 9224...")
    if not bridge.is_alive():
        print("Opera Neon is not running on port 9224!")
        return

    print("Submitting consultation prompt to ChatGPT...")
    res = await bridge.consult_ai(engine="chatgpt", prompt=PROMPT, timeout_seconds=90)
    print("STATUS:", res.get("status"))
    response_text = res.get("response", "")
    print("RESPONSE LEN:", len(response_text))
    
    with open("chatgpt_phase8_9_11_consultation.txt", "w", encoding="utf-8") as f:
        f.write(response_text)
    print("Wrote chatgpt_phase8_9_11_consultation.txt")

if __name__ == "__main__":
    asyncio.run(main())
