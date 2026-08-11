# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:
  - Nguyễn Hoàng Long (`2A202601134`) — Member 3: Dashboard, SLO & Alerts
  - Nguyễn Trọng Đăng Khoa (`2A202601964`) — Member 1: Logging & PII

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (76 records; 0 missing required fields; 0 missing enrichment; 0 PII leaks; 37 unique correlation IDs)
- Tổng số traces:
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID: `submission/evidence/checkpoint-1-correlation-headers.json` (2 requests, IDs `req-c5ea9abe` và `req-32414712`, response headers khớp response body)
- Evidence PII redaction: `submission/evidence/checkpoint-1-scrubbed-log-sample.json` và `submission/evidence/checkpoint-1-validate-logs.txt`
- Cách bảo vệ: middleware validate/tao `req-<8-hex>` và bind context cho toàn request; `user_id` chỉ ghi SHA-256 12 ký tự đầu. `summarize_text()` scrub preview, còn `scrub_event` scrub đệ quy payload và text trước `JsonlFileProcessor` render/ghi JSONL.
- Evidence trace waterfall: Langfuse trace waterfall (chat-response -> retrieve-context -> generate-response) được tạo bởi `app/agent.py`; xác thực trace cần restart API sau khi cập nhật endpoint regional trong `.env`.
- Giải thích một span đáng chú ý: `retrieve-context` là span RAG; trong challenge `rag_slow`, span này chứa độ trễ 2.5 giây từ `app/mock_rag.py:17-18`.

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Dashboard runtime: Streamlit đọc `data/logs.jsonl`, dùng time range 60 phút và tự refresh 30 giây. Sáu panel gồm latency P50/P95/P99, traffic, error rate/breakdown, cost, input/output tokens và quality proxy.
- Evidence dashboard baseline: [`evidence/dashboard_screenshot.png`](evidence/dashboard_screenshot.png)
- Evidence dashboard khi thử `rag_slow`: [`evidence/incident_response.png`](evidence/incident_response.png)
- Evidence dashboard challenge K4: [`evidence/challenge_dashboard.png`](evidence/challenge_dashboard.png)
- Evidence validator: [`evidence/dashboard_validation.txt`](evidence/dashboard_validation.txt)
- SLO đã chọn và lý do:
  - `latency_p95_ms <= 2000`, target 99.5%: dùng ngưỡng nghiêm ngặt từ challenge K4 `day13-k4-observability-v1`.
  - `error_rate_pct <= 2`, target 99.0%: giới hạn tỷ lệ request thất bại ảnh hưởng trực tiếp người dùng.
  - `daily_cost_usd <= 2.5`: kiểm soát ngân sách của lab.
  - `quality_score_avg >= 0.75`, target 95.0%: ngăn tối ưu latency/cost làm giảm chất lượng tối thiểu.
- Alert rules:
  - `HighLatencyAlert`: P95 lớn hơn 2000 ms trong 5 phút, severity warning.
  - `HighErrorRateAlert`: error rate lớn hơn 2% trong 3 phút, severity critical.
  - `CostBudgetAlert`: cost lớn hơn 2.5 USD trong 1 giờ, severity warning.
- Runbook: [`../docs/alerts.md`](../docs/alerts.md); evidence tại [`evidence/runbook_example.png`](evidence/runbook_example.png).
- Kiểm thử runtime: baseline P95 `1179 ms`; khi bật `rag_slow`, dashboard ghi nhận P95 `3618 ms`, vượt ngưỡng K4 2000 ms. Incident được tắt sau kiểm thử.

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1` (K4; incident `rag_slow`; feature `monitoring`; threshold `2000 ms`)
- Triệu chứng từ metrics: trước recovery, `latency_p95=3391 ms`, `latency_p99=3436 ms`; challenge logs ghi `response_sent.latency_ms` khoảng `3333-3436 ms`.
- Trace ID liên quan: trace IDs cần lấy từ Langfuse sau khi API được restart với `LANGFUSE_HOST=https://jp.cloud.langfuse.com`; correlation IDs chứng minh liên kết log gồm `req-0c24e568` (`k4-challenge-s01`) và `req-03726153` (`k4-challenge-s02`).
- Log line/correlation ID liên quan: `data/logs.jsonl`, các bản ghi `response_sent` của `k4-challenge-s01..s05`; ví dụ `req-0c24e568` latency `3391 ms`, `req-03726153` latency `3436 ms`.
- Root cause: `app/mock_rag.py:17-18` gọi `time.sleep(2.5)` khi `STATE["rag_slow"]` bật, làm chậm span RAG.
- Fix action: disable incident qua `/incidents/rag_slow/disable`; sau recovery fresh responses khoảng `797-856 ms`, dưới `2000 ms`.
- Preventive measure: đặt timeout/circuit breaker cho retrieval, cảnh báo p95 theo feature ở `2000 ms`, và nối metric -> trace -> correlation log trong runbook.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Hoàng Long (`2A202601134`) | Dashboard 6 panel, SLO K4, alert rules, runbooks và evidence runtime | `bf1e225` | Dùng Metrics → Traces → Logs; đặt alert theo triệu chứng/SLO và kiểm chứng dashboard bằng incident. |
  
| Nguyễn Trọng Đăng Khoa (`2A202601964`) | Logging & PII: correlation ID middleware, structured JSON logging, recursive PII redaction, request-context enrichment và evidence validation | `1494368`, `667f47e` | Bảo vệ dữ liệu nhạy cảm bằng hash/redaction và dùng correlation ID để nối logs với traces. |
