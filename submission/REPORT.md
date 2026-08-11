# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

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

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Member 3 | Dashboard 6 panel, SLO K4, alert rules, runbooks và evidence runtime | Commit Member 3 | Dùng Metrics → Traces → Logs; đặt alert theo triệu chứng/SLO và kiểm chứng dashboard bằng incident. |
