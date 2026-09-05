import asyncio
import json
import os
import shutil
import sys
import time
import urllib.request
import websockets

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

TARGET_ID = "4E901E829F8830F38A32B509A1F7C75E"
OBSIDIAN_DIR = r"C:\Users\nswcl\OneDrive\Documents\Obsidian Vault\00_LAR_OS"
LOCAL_CONTEXT_FILE = "SESSION_CONTEXT_SUMMARY.md"

PROMPT = """Chào GPT! Mình có một tin vui và một bài toán kiến trúc mới cần tham vấn bạn:

1. BÁO CÁO CA ĐIỀU TRỊ THÀNH CÔNG: BỆNH NHÂN ANTIGRAVITY IDE ĐÃ XUẤT VIỆN (HOSPITAL.MD):
- Triệu chứng cũ: Mở Antigravity IDE nhưng hoàn toàn không hiện cửa sổ (MainWindowHandle = 0), không nạp renderer, Language Server timeout.
- Nguyên nhân gốc (được tìm ra qua hội chẩn Jules session sessions/7480572946196687105):
  + Cây thư mục `resources\\app` bị thiếu hoàn toàn thư mục `out` (chứa entry point `out\\main.js`). Node ESM loader bị crash `ERR_MODULE_NOT_FOUND` ngay khi bootstrap trước khi kịp gọi API tạo BrowserWindow.
  + Lý do giải nén dang dở: Vào thời điểm auto-update lúc 10:52:25, có 27 tiến trình `Antigravity IDE.exe` zombie đang chạy ngầm chiếm giữ Mutex hệ thống (`AntigravityIDEMutex`) và lock file nhị phân, khiến bộ cài Inno Setup bị chặn ghi đè.
- Quá trình phẫu thuật:
  + Backup phòng vệ thư mục `resources`.
  + Dừng triệt để 27 tiến trình zombie để giải phóng Mutex và file handles.
  + Chạy installer chính thức in-place với cờ `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART`.
  + Nghiệm thu: `resources\\app\\out\\main.js` (15,040,636 bytes) tái lập đầy đủ. Toàn bộ profile, conversation và extensions bảo tồn 100%.
  + Kiểm thử lâm sàng: MainWindowHandle = 11601146 (GUI render thành công), Language Server PID 29412 kết nối tốt, renderer.log 7.3KB mượt mà.
- Lưu ý: LAR-OS Gateway (port 18797) và Nuclear Watcher v3.6 hoàn toàn an toàn, đạt 20/20 Chaos & Stress test (100%).

2. BRAINSTORM CÁC CƠ CHẾ "PHÒNG BỆNH" (PREVENTIVE MEASURES):
Nhờ bạn cùng brainstorm các giải pháp công nghệ để phòng bệnh triệt để, ngăn chặn vĩnh viễn tình trạng Inno Setup update bị zombie process lock file gây corrupt nhị phân trong tương lai:
- Cơ chế 1: Pre-Update Preflight Guard - Làm sao phát hiện/ngăn ngừa zombie processes trước khi Inno Setup chạy?
- Cơ chế 2: Binary Integrity Checker - Làm sao kiểm tra nhanh (<1ms) tính toàn vẹn của `resources\\app\\out\\main.js` khi boot và kích hoạt tự sửa lỗi nếu phát hiện hư hỏng?
- Cơ chế 3: Windows Mutex (`AntigravityIDEMutex`) & Zombie process hygiene cho ứng dụng Electron / Inno Setup.
- Cơ chế 4: Tích hợp vào LAR-OS Nuclear Watcher / Gateway ra sao để giữ vững nguyên tắc Zero-SaaS và RAM siêu nhẹ (<15MB)?

3. TỔNG KẾT NGỮ CẢNH HỆ THỐNG (CONTEXT SUMMARY):
Nhờ bạn tổng kết ngắn gọn cập nhật trạng thái mới nhất của hệ thống (Antigravity IDE Recovered + Phase 12.1 Nuclear Hardening 100% + Golden Invariants) để mình lưu ngay vào Obsidian Vault cho user theo dõi."""

async def main():
    print("[1] Activating Opera Neon tab...")
    try:
        req = urllib.request.Request(f"http://127.0.0.1:9224/json/activate/{TARGET_ID}")
        with urllib.request.urlopen(req) as resp:
            print("  -> Tab activation:", resp.read().decode())
    except Exception as e:
        print("  -> Activate error:", e)

    with urllib.request.urlopen("http://127.0.0.1:9224/json") as r:
        tabs = json.loads(r.read().decode("utf-8"))
    t = [x for x in tabs if x.get("id") == TARGET_ID]
    if not t:
        print("[-] Target tab not found!")
        return
    ws_url = t[0].get("webSocketDebuggerUrl")

    async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
        print("[2] Connected to WebSocket debugger. Bringing page to front...")
        await ws.send(json.dumps({"id": 1, "method": "Page.bringToFront"}))
        await asyncio.sleep(0.5)

        # Record baseline assistant turns
        count_js = """
        (function() {
            var turns = document.querySelectorAll('div[data-message-author-role="assistant"], article');
            return turns.length;
        })()
        """
        await ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {"expression": count_js, "returnByValue": True}}))
        baseline_count = 0
        while True:
            raw = await asyncio.wait_for(ws.recv(), 5.0)
            msg = json.loads(raw)
            if msg.get("id") == 2:
                baseline_count = msg.get("result", {}).get("result", {}).get("value") or 0
                print(f"  -> Baseline assistant turns: {baseline_count}")
                break

        # Inject prompt into the bottom-most composer strictly
        escaped_prompt = json.dumps(PROMPT)
        inject_js = f"""
        (async function() {{
            // 1. Smooth scroll to the bottom of the page
            window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }});
            await new Promise(r => setTimeout(r, 500));

            // 2. Select bottom canonical chat composer
            var composer = document.querySelector('form #prompt-textarea') || document.querySelector('#prompt-textarea');
            if (!composer) return JSON.stringify({{ ok: false, error: "Composer not found" }});

            composer.scrollIntoView({{ behavior: 'smooth', block: 'end' }});
            composer.focus();

            // Clear any draft
            document.execCommand('selectAll', false, null);
            document.execCommand('delete', false, null);

            // Insert prompt via execCommand to trigger React / ProseMirror state
            document.execCommand('insertText', false, {escaped_prompt});

            // Fallback input dispatch
            composer.dispatchEvent(new Event('input', {{ bubbles: true }}));
            composer.dispatchEvent(new Event('change', {{ bubbles: true }}));

            await new Promise(r => setTimeout(r, 400));

            // 3. Find send button and click
            var form = composer.closest('form') || composer.parentElement;
            var sendBtn = form.querySelector('button[data-testid="send-button"]') ||
                          form.querySelector('button.composer-submit-btn') ||
                          form.querySelector('button.composer-submit-button-color');

            if (sendBtn && !sendBtn.disabled && sendBtn.getAttribute('aria-disabled') !== 'true') {{
                sendBtn.click();
                return JSON.stringify({{ ok: true, method: "button_click" }});
            }}

            // Fallback: Dispatch Enter keydown
            var enterEvt = new KeyboardEvent('keydown', {{
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13,
                bubbles: true,
                cancelable: true
            }});
            composer.dispatchEvent(enterEvt);
            return JSON.stringify({{ ok: true, method: "enter_fallback" }});
        }})()
        """

        print("[3] Injecting prompt into bottom composer with smooth scroll...")
        await ws.send(json.dumps({
            "id": 3,
            "method": "Runtime.evaluate",
            "params": {"expression": inject_js, "returnByValue": True, "awaitPromise": True}
        }))

        while True:
            raw = await asyncio.wait_for(ws.recv(), 10.0)
            msg = json.loads(raw)
            if msg.get("id") == 3:
                res_val = msg.get("result", {}).get("result", {}).get("value")
                print(f"  -> Injection status: {res_val}")
                break

        print("[4] Monitoring ChatGPT response stream...")
        start_time = time.time()
        last_text = ""
        stable_count = 0
        has_streamed = False

        while time.time() - start_time < 180:
            await asyncio.sleep(2.5)
            # Re-activate tab and bring to front so stream is never throttled
            await ws.send(json.dumps({"id": 10, "method": "Page.bringToFront"}))

            scrape_js = """
            (function() {
                var stopBtn = document.querySelector('button[data-testid="stop-button"], [aria-label*="Dừng"], [aria-label*="Stop"]');
                var turns = Array.from(document.querySelectorAll('div[data-message-author-role="assistant"], article'));
                var lastTurn = turns.length > 0 ? turns[turns.length - 1] : null;
                var text = "";
                if (lastTurn) {
                    var md = lastTurn.querySelector('.markdown') || lastTurn;
                    text = md.innerText.trim();
                }
                return JSON.stringify({
                    is_streaming: Boolean(stopBtn),
                    turns_count: turns.length,
                    text: text
                });
            })()
            """
            scrape_id = int(time.time() * 1000) % 100000
            await ws.send(json.dumps({
                "id": scrape_id,
                "method": "Runtime.evaluate",
                "params": {"expression": scrape_js, "returnByValue": True}
            }))

            data = None
            try:
                while True:
                    raw = await asyncio.wait_for(ws.recv(), 4.0)
                    m = json.loads(raw)
                    if m.get("id") == scrape_id:
                        val = m.get("result", {}).get("result", {}).get("value")
                        if val:
                            data = json.loads(val)
                        break
            except asyncio.TimeoutError:
                continue

            if not data:
                continue

            curr = data.get("text", "")
            streaming = data.get("is_streaming", False)
            turns_count = data.get("turns_count", 0)

            if streaming:
                has_streamed = True
                print(f"  ... Streaming response ({len(curr)} chars) ...")

            if (turns_count > baseline_count or has_streamed) and curr:
                if curr == last_text and not streaming:
                    stable_count += 1
                    if stable_count >= 2:
                        print(f"[✓] ChatGPT Response Completed ({len(curr)} chars) in {round(time.time() - start_time, 1)}s!")
                        with open("chatgpt_hospital_response.md", "w", encoding="utf-8") as f:
                            f.write(curr)
                        print("  -> Saved response to chatgpt_hospital_response.md")
                        
                        # Now update Obsidian Vault session summary
                        update_session_summary(curr)
                        return curr
                else:
                    stable_count = 0
                    last_text = curr

        if last_text:
            print(f"[!] Reached timeout, capturing partial response ({len(last_text)} chars)")
            with open("chatgpt_hospital_response.md", "w", encoding="utf-8") as f:
                f.write(last_text)
            update_session_summary(last_text)
            return last_text

        print("[-] Timeout waiting for response")
        return ""

def update_session_summary(gpt_response: str):
    print("[5] Synchronizing updated session context summary to Obsidian Vault...")
    summary_content = f"""# LAR-OS & ANTIGRAVITY SESSION CONTEXT SUMMARY
**Updated**: {time.strftime('%Y-%m-%d %H:%M:%S')} (Local Time)
**Status**: ANTIGRAVITY IDE CURED & DISCHARGED | LAR-OS PHASE 12.1 NUCLEAR HARDENING 100%

---

## 1. Executive Summary & Clinical Discharge
- **Antigravity IDE (v2.5.5)**: 
  - Restored from severe bootstrap crash (`ERR_MODULE_NOT_FOUND` on `out\\main.js`).
  - Cause: 27 zombie `Antigravity IDE.exe` processes holding `AntigravityIDEMutex` blocked Inno Setup extraction.
  - Fix: Stopped zombies -> Ran in-place installer (`/VERYSILENT /SUPPRESSMSGBOXES /NORESTART`) -> Re-established `out\\main.js` (15MB). User profile/extensions 100% preserved.
  - Verified: `MainWindowHandle = 11601146`, Language Server PID `29412`, renderer log clean.
- **LAR-OS Gateway v3.6 & Nuclear Watcher v3.6**:
  - PID reuse protection via native Windows `kernel32.GetProcessTimes` (`ctypes`).
  - Isolated SOS subprocess execution (`gmail_spark_sender.py --send-sos`).
  - Stale graceful flag handling & heartbeat read hysteresis.
  - Chaos & Stress Test Suite: 20 / 20 PASSED (100.0%).

---

## 2. ChatGPT Brainstorming: Preventive Measures ("Phòng Bệnh")
The following preventive strategies and architectural roadmap were brainstormed with ChatGPT:

{gpt_response}

---

## 3. Golden Invariants
- Gateway RAM: < 45MB (Current ~35MB)
- Watcher RAM: < 15MB (Current ~8.4MB)
- Idle CPU: 0.0%
- SQLite: < 2MB (Current ~120KB)
- Zero SaaS / Zero Docker dependencies.
"""
    with open(LOCAL_CONTEXT_FILE, "w", encoding="utf-8") as f:
        f.write(summary_content)
    print(f"  -> Written local {LOCAL_CONTEXT_FILE}")

    if os.path.exists(OBSIDIAN_DIR):
        obsidian_target = os.path.join(OBSIDIAN_DIR, LOCAL_CONTEXT_FILE)
        shutil.copyfile(LOCAL_CONTEXT_FILE, obsidian_target)
        print(f"  -> Synced to Obsidian Vault: {obsidian_target}")

if __name__ == "__main__":
    asyncio.run(main())
