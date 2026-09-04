import sys
import json
import asyncio
from opera_neon_ai_bridge import OperaNeonBridge

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

async def main():
    bridge = OperaNeonBridge()
    if not bridge.is_alive():
        print("[-] Opera Neon is not reachable on CDP port 9224")
        return

    prompt = (
        "Chào bạn, tôi là hệ thống trợ lý kỹ thuật cho người dùng Jun (Bảo). "
        "Chúng tôi đang xây dựng tầng dự phòng (Failover Tier) cho LAR-OS Gateway khi cả 5 API key Gemini Pro chính bị cạn quota. "
        "Người dùng nhờ bạn phân tích và đưa ra quyết định chọn 1 trong 2 phương án sau:\n\n"
        "Phương án A: Sử dụng 'CLIProxyAPI' (Go backend, router-for-me/CLIProxyAPI).\n"
        "- Ưu điểm: Cực kỳ gọn nhẹ (<30MB RAM), viết bằng Go thuần, chạy ngầm làm Windows Daemon/Tray không tốn tài nguyên.\n"
        "- Cơ chế: Dùng Antigravity OAuth (CloudCode developer endpoint) xoay vòng multi Gmail round-robin, tự động refresh token ngầm 100% không cần UI.\n"
        "- Phù hợp: Hoàn hảo cho backend API headless, gateway tự động chuyển mạch khi 5 key chính trả về 429.\n\n"
        "Phương án B: Sử dụng '9Router' (Next.js + Go, decolua/9router).\n"
        "- Ưu điểm: Có Web Dashboard trực quan tại localhost:20128, tích hợp RTK Token Saver nén prompt 20-40%, hỗ trợ thêm Kiro AI và OpenCode Free.\n"
        "- Nhược điểm: Chạy Node/Next.js nặng hơn về RAM/CPU, cần thao tác quản trị qua giao diện web.\n\n"
        "Câu hỏi: Với mục tiêu phục vụ Gateway chạy 24/7 cho đa thiết bị (Termux Android, PC), ưu tiên tính ổn định cao, độ trễ thấp, tiết kiệm tài nguyên máy và tự động hóa tuyệt đối khi failover, bạn khuyên Jun nên chọn Phương án nào? Hãy phân tích súc tích và đưa ra lựa chọn quyết định dứt khoát."
    )

    print("[*] Sending consultation to ChatGPT in Opera Neon...")
    res = await bridge.consult_ai("chatgpt", prompt, timeout_seconds=90)
    print("\n=== KẾT QUẢ TỪ CHATGPT ===")
    print(res.get("text", json.dumps(res, ensure_ascii=False, indent=2)))

if __name__ == "__main__":
    asyncio.run(main())
