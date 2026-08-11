# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

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

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

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
| | | | |
