import asyncio
import sys
import json
import time
from opera_neon_ai_bridge import get_bridge

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

PROMPT = """
Chào GPT! User vừa yêu cầu một bài toán cực kỳ quan trọng cho LAR-OS Gateway v3.5:

ĐỀ BÀI: Thiết kế cơ chế "NUCLEAR EVENT" (Sự Cố Hạt Nhân / Báo Động Đỏ Tối Thượng) cho LAR-OS.
Bao gồm:
1. Khi nào được coi là một "Nuclear Event" (Crash thảm họa) để kích hoạt gửi thư cầu cứu?
   - Phân biệt giữa failover bình thường (vài tài khoản Gemini bị 429 tạm thời) vs True Nuclear Crash.
   - Các điều kiện kích hoạt cụ thể là gì? (ví dụ: All 5 Gemini dead + Tier-4 dead + Gateway 100% cạn đường sống; hoặc Process Gateway bị crash/OOM/OS kill đột ngột; hoặc Event loop bị hang hoàn toàn > 30s).
2. Làm sao TỰ ĐỘNG IDENTIFY (phát hiện) được Antigravity / Gateway đang bị crash?
   - Cơ chế nào đáng tin cậy nhất cho máy cá nhân: Dead Man's Switch, Heartbeat ping, Watchdog sidecar, hay Unhandled Exception Hook (`sys.excepthook`, `atexit`, signal handler)?
   - Nếu bản thân tiến trình Gateway chết đột ngột (Segfault, Memory limit, Windows taskkill), tiến trình nào còn sống để phát hiện và gửi mail?
3. Gửi thư cầu cứu qua Spark (Gmail Spark Sender):
   - Hiện hệ thống đã có sẵn `gmail_spark_sender.py` (dùng Opera Neon CDP port 9224 gửi mail tới `thuaquan228@gmail.com` để user nhận qua app Spark trên mobile).
   - Thiết kế luồng gửi thư SOS khẩn cấp sao cho đảm bảo gửi thành công ngay cả khi Gateway chính đã sập.
4. Soạn sẵn "mấu nối" (Pre-formatted SOS Email Payload):
   - Nội dung thư SOS nên trình bày thế nào cho chuẩn Mobile Spark:
     + Tiêu đề báo động đỏ nổi bật.
     + Lý do crash chính xác, stack trace tóm tắt.
     + Trạng thái tài nguyên (RAM, CPU, Last SQLite telemetry events).
     + Lệnh cứu hộ khẩn cấp 1-click (One-click recovery command trên Termux/SSH hoặc PowerShell).
5. NHỜ GPT THAM KHẢO THÊM TRÊN MẠNG (Search web):
   - Nhờ bạn search trên mạng về các mẫu kiến trúc "Dead man's switch for edge daemon / local AI", "Lightweight crash notifier without external SaaS", "Out-of-band alerting for home servers", trích dẫn các best practice hoặc repo GitHub hữu ích nếu có.
   - Ràng buộc bất biến: RAM < 45MB, CPU ~0%, KHÔNG dùng SaaS trả phí, KHÔNG dùng Docker/Prometheus.

LƯU Ý: Nếu GPT cần xem chi tiết nội dung code của bất kỳ file nào trong dự án (ví dụ `lar_os_gateway.py`, `gmail_spark_sender.py`, `anti_crash_guard.py`, `chaos_test_suite.py`, v.v.), bạn cứ yêu cầu rõ tên file, mình sẽ trích xuất và gửi nguyên văn ngay lập tức!
"""

async def main():
    bridge = get_bridge()
    print("Checking Opera Neon CDP on 9224...")
    if not bridge.is_alive():
        print("[-] Opera Neon is not running on port 9224!")
        return

    print("Submitting Nuclear Event consultation prompt to ChatGPT...")
    res = await bridge.consult_ai(engine="chatgpt", prompt=PROMPT, timeout_seconds=95)
    print("STATUS:", res.get("status"))
    response_text = res.get("response", "")
    print("INITIAL RESPONSE LEN:", len(response_text))
    
    with open("chatgpt_nuclear_consultation.txt", "w", encoding="utf-8") as f:
        f.write(response_text)
    print("Saved chatgpt_nuclear_consultation.txt")

if __name__ == "__main__":
    asyncio.run(main())
