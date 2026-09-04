import asyncio
import sys
import json
import time
from pathlib import Path
from opera_neon_ai_bridge import get_bridge

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

DIR = Path(__file__).parent
with open(DIR / "anti_crash_guard.py", "r", encoding="utf-8") as f:
    anti_crash_content = f.read()

with open(DIR / "gmail_spark_sender.py", "r", encoding="utf-8") as f:
    gmail_spark_content = f.read()

PROMPT = f"""
Chào bạn! Mình gửi bạn nguyên văn 2 file bạn vừa yêu cầu để cùng thiết kế cơ chế "NUCLEAR EVENT" tối thượng cho LAR-OS:

========================
FILE 1: anti_crash_guard.py
========================
```python
{anti_crash_content}
```

========================
FILE 2: gmail_spark_sender.py
========================
```python
{gmail_spark_content}
```

------------------------
YÊU CẦU THAM VẤN CHI TIẾT TỪ USER:
User vừa chỉ đạo:
"ok, và nếu gpt yêu cầu file thì nhớ đưa cho bạn ấy nhé. đồng thời tham vấn gpt cho nuclear event, gồm gửi thư cầu cứu mình qua spark, soạn sẵn mấu nối, khi nào crash thì gửi và làm sao tự indentify dc anti đang bị crash. nhờ bạn ấy tham khảo trên mạng thêm"

Nhờ bạn đào sâu, tra cứu thêm các best practice trên mạng (web search: dead man's switch patterns, out-of-band crash alert, python supervisor failure cascade prevention), và chốt thiết kế chi tiết cho các vấn đề sau:

1. BOUNDARY & KIẾN TRÚC PHÁT HIỆN CRASH (Làm sao tự identify được Antigravity / Gateway đang bị crash?):
   - Đánh giá `anti_crash_guard.py` hiện tại: Nó mới chỉ là audit script chạy 1 lần. Cần nâng cấp thành `lar_os_nuclear_watcher.py` (hoặc daemon độc lập) như thế nào?
   - Cơ chế phát hiện: Kết hợp giữa Heartbeat atomic file (Gateway ghi mỗi 5s) + External Watchdog PID checking (kiểm tra mỗi 10s) + Crash forensic logger (`faulthandler` + `sys.excepthook` ghi ra file `crash/latest.txt`).
   - Xử lý các ca khó: Windows `taskkill /F`, OOM killer, Python native segfault, asyncio event loop hang (freeze hoàn toàn).

2. ĐIỀU KIỆN KÍCH HOẠT (Khi nào crash thì gửi SOS?):
   - Xác định chính xác ma trận: khi nào thì trigger NUCLEAR SOS ngay lập tức, khi nào thì có grace period (ví dụ 10s), khi nào là bình thường (cooldown / circuit breaker) tuyệt đối KHÔNG gửi spam.
   - Cơ chế Deduplication (Chống spam email liên tục vào Spark khi Gateway sập).

3. GỬI THƯ CẦU CỨU QUA SPARK (Tối ưu hóa `gmail_spark_sender.py` cho tình huống khẩn cấp):
   - Khi Gateway chết, Watchdog sẽ gọi `GmailSparkSender` độc lập ra sao?
   - Nếu Opera Neon (CDP port 9224) đang không mở tab Gmail, hoặc Neon bị đóng, Watchdog có cơ chế tự mở lại Neon headless/background hoặc fallback ra sao?
   - Đảm bảo gửi tới `thuaquan228@gmail.com` để user nhận push notification tức thì trên app Spark (iOS / Android).

4. SOẠN SẴN MẤU NỐI (Pre-formatted SOS Email Payload):
   - Thiết kế mẫu nối dữ liệu chuẩn (HTML + Text) để đọc cực kỳ rõ ràng trong 5 giây trên màn hình điện thoại Spark:
     + Subject chuẩn, gây chú ý mạnh (🚨 [LAR-OS NUCLEAR EVENT] ...).
     + Trích xuất đúng 8 dòng lỗi quan trọng nhất từ `crash/latest.txt`.
     + Trạng thái tài nguyên cuối cùng (RAM, CPU, SQLite WAL).
     + Mấu nối "One-click rescue command": câu lệnh PowerShell và Termux SSH sẵn sàng để user copy/paste restart hệ thống.

5. THAM KHẢO THÊM TRÊN MẠNG:
   - Các kỹ thuật dead-man's switch / fail-silent alerting / crash notification phổ biến trên các hệ thống micro-service / edge daemon tự lưu trữ (self-hosted).

Ràng buộc tối thượng:
- CPU idle ~0%, RAM tổng < 45MB.
- Không dùng SaaS bên thứ 3 tính phí.
- Chạy tin cậy trên Windows 11.
"""

async def main():
    bridge = get_bridge()
    print("Checking Opera Neon CDP on 9224...")
    if not bridge.is_alive():
        print("[-] Opera Neon is not running on port 9224!")
        return

    print(f"Submitting follow-up prompt (size: {len(PROMPT)} chars) with source files to ChatGPT...")
    res = await bridge.consult_ai(engine="chatgpt", prompt=PROMPT, timeout_seconds=120)
    print("STATUS:", res.get("status"))
    response_text = res.get("response", "")
    print("RESPONSE LEN:", len(response_text))
    
    with open(DIR / "chatgpt_nuclear_part2_consultation.txt", "w", encoding="utf-8") as f:
        f.write(response_text)
    print("Saved chatgpt_nuclear_part2_consultation.txt")

if __name__ == "__main__":
    asyncio.run(main())
