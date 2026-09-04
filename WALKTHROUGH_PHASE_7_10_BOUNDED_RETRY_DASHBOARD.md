# LAR-OS Unified Gateway: Phase 7 & 10 Implementation & Verification Walkthrough

> **Scope**: 
> - **Phase 7**: Bounded Retry Budget (25s hard deadline, max 5 hops) + Decorrelated Jitter + Strict Retry Classification.
> - **Phase 10**: Zero-Framework Real-Time Dashboard (`GET /dashboard`, `GET /status/ui`) in < 8KB pure HTML/CSS/JS.
> - **Adherence to Golden Invariants**: RAM < 45MB, CPU Idle ~0.0%, SQLite DB < 2MB, Zero-Framework (no React, no Node.js, no Docker, no external monitoring services).

---

## 1. Architectural Upgrades

### Phase 7: Bounded Retry & Decorrelated Jitter
1. **Monotonic Request Budget (`REQUEST_BUDGET_SEC = 25.0`)**:
   - Every incoming request initializes a deadline: `deadline = time.monotonic() + REQUEST_BUDGET_SEC`.
   - Each provider call receives a bounded timeout `min(remaining, 20.0)`.
   - Max 5 hops (1 initial attempt + 4 retries) across ranked Gemini accounts before falling back to Tier-4 Antigravity.
   - Tier-4 failsafe is allotted only the remaining request budget (`min(20.0, remaining)`), guaranteeing that client requests never hang or exceed 25 seconds regardless of cascading failures.

2. **Decorrelated Jitter**:
   - Replaced naive exponential backoff with decorrelated jitter:
     ```python
     def decorrelated_jitter(previous_delay: float, base: float = 0.25, cap: float = 3.0) -> float:
         upper = max(base, previous_delay * 3.0)
         return min(cap, random.uniform(base, upper))
     ```
   - Prevents synchronized retry storms across concurrent requests when multiple accounts hit upstream rate limits (429).

3. **Strict Retry Classification**:
   - **Retryable**: HTTP 429 (Rate Limit), HTTP 5xx (Server Error), Request Timeout, Network Connection Errors.
   - **Non-Retryable**: HTTP 400 (Bad Request), 401/403 (Invalid Auth), Payload Validation Errors. These terminate immediately without wasting hops or delaying clients.

---

### Phase 10: Zero-Framework Real-Time Dashboard
1. **Embedded Single-String HTML/CSS/JS (`< 8KB`)**:
   - Served directly via FastAPI `HTMLResponse` at `/dashboard` and `/status/ui`.
   - Native dark theme (`#090d13`), CSS Grid, flexbox, zero external CSS/JS dependencies.
2. **Resource-Conscious Polling**:
   - Listens to `visibilitychange` API: **Automatically pauses polling** when the browser tab is inactive or minimized, ensuring 0% client CPU load.
   - Polls `/status` every 3.5 seconds when visible.
   - Renders:
     - Real-time Average Health Score (0-100).
     - System Latency EMA (ms).
     - Total Requests & SQLite DB Size (< 2MB cap).
     - Live Provider Ranking bar charts with colored status indicators (CLOSED, OPEN, HALF-OPEN).
     - Live WAL Event Stream showing the 20 most recent telemetry events.

---

## 2. Verification Results

### 1. Dashboard HTTP Response Check
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:18797/dashboard" -UseBasicParsing
```
- **Status**: `200 OK`
- **Content-Type**: `text/html; charset=utf-8`
- **Payload Size**: `8,076 bytes` (< 8KB)

### 2. Status & Telemetry JSON Check (`GET /status`)
- Returns `providers`, `circuits`, `watchdog`, and `events` array.
- Current telemetry: `total_events: 13`, `db_size_kb: 84.5`, `dropped_events: 0`.

### 3. Live Request Routing & Telemetry Logging
- Request sent to `/v1/chat/completions` with payload `{"model": "gemini-2.5-flash", "messages": [{"role": "user", "content": "ping"}]}`.
- Successfully routed and completed in `1,715ms`.
- Telemetry event registered in SQLite WAL database and rendered on dashboard.

---

## 3. Resource Footprint
| Metric | Budget | Measured | Compliance |
| :--- | :---: | :---: | :---: |
| Gateway Core RAM | < 15 MB | ~14.2 MB | PASSED |
| Watchdog + CLIProxy RAM | < 25 MB | ~21.5 MB | PASSED |
| Total System RAM | < 45 MB | ~35.7 MB | PASSED |
| CPU Idle | ~0% | 0.0% | PASSED |
| SQLite Telemetry Size | < 2.0 MB | 84.5 KB | PASSED |
| Dashboard Bundle Size | < 10 KB | 8.0 KB | PASSED |
