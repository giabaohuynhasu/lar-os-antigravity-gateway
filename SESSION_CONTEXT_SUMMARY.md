# LAR-OS ARCHITECTURAL CONTEXT & STATE SUMMARY (V3.5 -> V3.6)
**Thời điểm tổng kết**: 2026-09-05 06:15:00 (Local Time)
**Tác giả**: Gia Bao Huynh (Jun) / Antigravity
**Tư vấn & Audit**: ChatGPT (OpenAI) qua Opera Neon CDP (cổng 9224)
**Trạng thái**: Phase 12 Nuclear Event Protocol hoàn tất 100% (Commit `61c2473`)
**Độ bền Control-Plane**: Đạt 88% - 92% (theo đánh giá độc lập của ChatGPT)

---

## 1. Trạng Thái Hệ Thống Toàn Diện (Phases 1 - 12)

LAR-OS Gateway đã hoàn thiện toàn bộ 12 Phase nền tảng với độ ổn định và khả năng tự hồi phục cao (*Control-plane Hardening*):

1. **Phase 1 & 2 (Supervised 4-Tier Redundancy & Self-Healing)**:
   - **Tier 1**: In-Memory Bounded LRU Cache (tối đa 50 mục, TTL 60s, 0ms, 0 quota).
   - **Tier 2**: Multi-Account Primary Pool (5 tài khoản Google AI Pro với 3-State Circuit Breaker, tự động cooldown 60s khi 429).
   - **Tier 3**: Opera Neon CDP (cổng 9224, ChatGPT/Claude qua DOM Token Saver AXI).
   - **Tier 4**: Antigravity Free CLIProxyAPI (`cli-proxy-api.exe`, cổng 18798) tự hồi sinh qua Watchdog khi sập.
2. **Phase 3 & 4 (Adaptive Health Scoring & Latency EMA)**:
   - Công thức tính điểm: $\text{Score} = 100 - \min(\text{failures} \times 10, 40) - \min(\text{latency\_ema} / 100, 40)$.
   - $\alpha = 0.2$ cho Exponential Moving Average.
   - Dynamic Priority Routing: Luôn ưu tiên tài khoản có điểm cao nhất; Score $\le 0$ chuyển mạch sang Tier 4.
3. **Phase 5 & 6 (Non-blocking SQLite WAL Telemetry & Event-driven Maintenance)**:
   - Ghi telemetry bất đồng bộ qua queue đa luồng không khóa (`queue.put_nowait()`), rớt log thay vì block request.
   - Bounded SQLite WAL (< 2MB, prune tự động khi vượt 50,000 dòng).
   - Kích thước thực tế quan sát: **~438 KB** (cực kỳ tinh gọn).
4. **Phase 7 & 10 (Bounded Retry, Decorrelated Jitter & Zero-Framework Dashboard)**:
   - Ngân sách toàn cục 25 giây (`REQUEST_BUDGET_SEC`), tối đa 5 hop failover.
   - Decorrelated Jitter tránh thảm họa thundering herd.
   - Phân loại retry: chỉ retry lỗi mạng/tạm thời (429, timeout, 502, 503), không retry lỗi cú pháp/401/403.
   - Dashboard HTML/CSS thuần cực nhẹ (< 10KB) tại `http://127.0.0.1:18797/dashboard`.
5. **Phase 8 & 9 (Deep Health Check & Process Self-Isolation)**:
   - L1 Socket connect non-blocking (0.15s) + L2 Upstream OAuth tracking.
   - Bọc `_isolated_provider_call` bảo vệ tuyệt đối FastAPI event loop khỏi mọi exception.
6. **Phase 11 (Comprehensive Chaos Testing C1 - C7)**:
   - Đạt **100% (7/7 tests passed)**: xác nhận liveness, failover, kill process tự hồi sinh, và ngân sách thời gian.
7. **Phase 12 (Nuclear Event Protocol & Out-of-Band Watchdog)**:
   - Bộ phát Heartbeat nguyên tử (`heartbeat.json`, chu kỳ 5s, ghi qua file `.tmp` + `os.replace`).
   - Crash forensics tự động (`faulthandler.enable()` + `sys.excepthook` ghi vào `crash/latest.txt`).
   - Tiến trình Nuclear Watcher độc lập (`lar_os_nuclear_watcher.py`, RAM ~8.4MB, CPU 0%).
   - Cứu hộ khẩn cấp 1-chạm (`recover_gateway.ps1`) cho PowerShell và Termux SSH.
   - Gửi thư báo động đỏ tới `thuaquan228@gmail.com` qua Opera Neon CDP và ứng dụng Spark trên điện thoại.
   - Đạt **100% (7/7 tests passed)** trên Chaos Test C8.

---

## 2. Bất Biến Vàng (Golden Invariants I1 - I19)

| Bất biến | Mô tả quy chuẩn | Đo lường thực tế | Trạng thái |
| :--- | :--- | :---: | :---: |
| **I1** | Gateway sống sót sau mọi ngoại lệ từ provider | 100% cô lập | **ĐẠT** |
| **I2** | Sập CLIProxyAPI không thể làm sập Gateway | Watchdog tự hồi sinh | **ĐẠT** |
| **I3** | Lỗi một provider không làm biến đổi trạng thái provider khác | Cô lập tuyệt đối | **ĐẠT** |
| **I4** | Không có socket nào bị treo vô hạn sau timeout | Timeout hữu hạn | **ĐẠT** |
| **I5** | Mọi tác vụ upstream đều có timeout định lượng | $\le 20\text{s}$ | **ĐẠT** |
| **I6** | Mỗi request có một ngân sách toàn cục đơn điệu (Hard Deadline) | $25\text{s}$ | **ĐẠT** |
| **I7** | Số bước nhảy tối đa (Hop Count) $\le 5$ | $\le 4\text{ hops}$ | **ĐẠT** |
| **I8** | Thời gian sleep retry không vượt ngân sách request còn lại | Dynamic clamp | **ĐẠT** |
| **I9** | Phân loại retry có giới hạn (chỉ retry lỗi tạm thời) | Enforced | **ĐẠT** |
| **I10** | Lỗi SQLite không phá vỡ routing của Gateway | Bypass an toàn | **ĐẠT** |
| **I11** | Hàng đợi telemetry đầy tự drop, không block request | Non-blocking | **ĐẠT** |
| **I12** | Sập Watchdog không kéo sập Gateway | Out-of-band | **ĐẠT** |
| **I13** | Không có vòng lặp busy polling (luôn dùng async/sleep/event) | Event-driven | **ĐẠT** |
| **I14** | CPU idle tiệm cận $0.0\%$ | $0.0\%$ | **ĐẠT TUYỆT ĐỐI** |
| **I15** | Gateway RAM tiêu chuẩn $< 45\text{ MB}$ | $\sim 35.0\text{ MB}$ | **ĐẠT TUYỆT ĐỐI** |
| **I15b**| Watcher RAM tiêu chuẩn $< 15\text{ MB}$ | $\sim 8.4\text{ MB}$ | **ĐẠT TUYỆT ĐỐI** |
| **I16** | 5 Gemini failures liên tiếp kích hoạt Tier 4 Antigravity | Fast fallback | **ĐẠT** |
| **I17** | Phục hồi CLIProxy không yêu cầu khởi động lại Gateway | Tự động | **ĐẠT** |
| **I18** | Chaos requests thành công trong $25\text{s}$ hoặc fail có kiểm soát | Bounded | **ĐẠT** |
| **I19** | **Hard Deadline Integrity**: Không request nào được sống quá $25\text{s}$ kể cả khi upstream/CDP/Tier4 bị treo | Enforced | **ĐẠT** |

---

## 3. Bản Thiết Kế Nâng Cấp Từ Audit Của ChatGPT

### 3.1. Phase 12.1 — Nuclear Hardening (Control-Plane Perfection)
ChatGPT chỉ ra 5 điểm polish control-plane để đạt độ bền 100%:
- **N12.1 — Process Identity (Chống PID Reuse trên Windows)**:
  Windows có thể tái sử dụng PID sau khi tiến trình chết. Bổ sung cặp `(PID, process_creation_time)` bằng Windows API `GetProcessTimes()` để xác thực tuyệt đối tiến trình sống.
- **N12.2 — Graceful Epoch (Chống Stale Graceful Flag)**:
  `graceful: true` phải thuộc về một incarnation cụ thể (`boot_id`). Nếu Gateway chết và không tự khởi động lại, cờ graceful cũ sau $30\text{s}$ không được quyền dập tắt trạng thái Nuclear.
- **N12.3 — Subprocess SOS Isolation (Cô lập kênh cứu hộ)**:
  Triệu gọi `gmail_spark_sender.py` dưới dạng tiến trình con riêng biệt với deadline cứng toàn cục $15\text{s}$ (`SOS_DEADLINE = 15s`). Ngăn ngừa hoàn toàn rủi ro WebSocket/CDP treo làm đứng vòng lặp kiểm tra của Watcher.
- **N12.4 — Heartbeat File Read Hysteresis**:
  Phân biệt lỗi đọc file nhất thời (do phần mềm diệt virus hoặc file indexer khóa tạm thời) thành `DEGRADED`, chỉ kích hoạt `NUCLEAR` khi không thể đọc liên tục $> 30\text{s}$.
- **N12.5 — Delivery State Tracking**:
  Tách bạch các trạng thái SOS: `ATTEMPTED`, `DELIVERED`, `FAILED`, `TIMED_OUT`. Một sự cố = đúng 1 sự cố logic, cho phép retry có giới hạn nếu gửi thất bại.

### 3.2. Bộ Thang Tải Trọng (Stress Ladder) & Chaos Tests Mới (C9 - C17)
- **Thang tải trọng (Stress Ladder)**:
  - `S1 (10 concurrent)`: Baseline tải nhẹ.
  - `S2 (25 concurrent)`: Tải trung bình.
  - `S3 (50 concurrent)`: Tải cao đột biến.
  - `S4 (100 concurrent)`: Điểm bão hòa (Saturation).
  - `S5 (250 concurrent)`: Khảo sát giới hạn gãy (Breakpoint).
  - `S6 (500 concurrent)`: Đo lường hành vi suy thoái có kiểm soát.
- **Soak Test 1 Giờ (T2 & T3)**:
  - Chạy 10-30 concurrent request liên tục 60 phút với lỗi ngẫu nhiên.
  - Kiểm tra tiêu chí: $\Delta\text{RAM} < +5\text{ MB}$, CPU idle giữ nguyên baseline, SQLite $< 2\text{ MB}$, không phát sinh tiến trình mồ côi hay socket rò rỉ.
- **Chaos Scenarios Mới (C9 - C17)**:
  - `C9`: Stale Graceful Heartbeat bypass khi Gateway không tự boot lại.
  - `C10`: Giả lập PID Reuse (PID tồn tại nhưng sai Creation Time).
  - `C11`: Xử lý Transient File Lock trên file heartbeat.
  - `C12`: Cổng CDP 9224 mở nhưng WebSocket bị đóng băng.
  - `C13`: Tiến trình gửi SOS bị treo (kiểm tra timeout 15s của Watcher).
  - `C14`: Tiến trình lạ chiếm cổng 18797 (script recovery xác minh đúng Gateway mới kill).
  - `C15`: Hard kill -9 Gateway trong lúc Watcher đang chạy.
  - `C16`: Giả lập Event-loop hang $> 30\text{s}$.
  - `C17`: Watcher chống chịu khi cả 5 Gemini pool, Tier 4 và CDP đồng loạt gặp sự cố.

---

## 4. Lộ Trình Tiến Hóa (Roadmap)

```text
LAR-OS v3.5 (Hiện tại)
  │
  ├── Phase 12.1: Nuclear Hardening (P0/P1 fixes: ProcessTimes, Stale Graceful, Subprocess SOS)
  │
  ├── Phase 12.5: Extreme Stress & Soak Test (Thang tải S1-S6, Soak test 60m, Chaos C9-C17)
  │
  ├── Phase 13: Windows Native SCM Service (Tích hợp Service Control Manager OS, 0MB RAM, tự hồi sinh cấp HĐH)
  │
  ├── Phase 14: Mobile Control Plane (Spark báo động đỏ + Termux SSH điều khiển từ xa)
  │
  ├── Phase 15: Semantic Prompt Cache (Token fingerprinting siêu nhẹ, không dùng Vector DB cồng kềnh)
  │
  └── Phase 16 & v4.0: Autonomous Agent Execution Kernel (Nền tảng thực thi tác vụ đa bước)
```

---

## 5. Danh Mục Quy Chuẩn Tham Vấn GPT (Consultation Rules)
1. **Smooth Bottom Scroll**: Khi kết nối Opera Neon CDP, luôn tự động cuộn mượt xuống đáy trang (`window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })`).
2. **Không Chỉnh Sửa Prompt Cũ**: Tuyệt đối chỉ nhập vào ô soạn thảo ở thanh cuối cùng (`form #prompt-textarea`), không bấm nút sửa (edit) trên các tin nhắn trước để người dùng theo dõi trực tiếp trong trình duyệt.
3. **Tổng Kết Ngữ Cảnh Chu Kỳ**: Sau mỗi lần tham vấn chuyên sâu, trích xuất bản tổng kết ngữ cảnh hệ thống và đồng bộ ngay vào Obsidian Vault (`00_LAR_OS/SESSION_CONTEXT_SUMMARY.md`).
