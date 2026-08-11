# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: K4-Sigmoid
- Repository URL: https://github.com/AIVIETNAM-AIO-FalconHeavyX/Day13-K4-Observability-sigmoid
- Commit SHA cuối: 5ba64725aaf0b5b4d51c28772973373d98d0f149
- Thành viên và vai trò:
  | Thành viên | Vai trò |
  |------------|---------|
  | Member 1 | Logging & PII |
  | Member 2 | Tracing & Prompt Version |
  | Member 3 | Dashboard, SLO & Alerts |
  | Member 4 | Incident Investigation & Report |

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 30/100 (middleware needs correlation ID fix)
- Tổng số traces: 0 (Langfuse tracing not connected during challenge)
- Số PII leak còn lại: 0 (PII scrubbing PASSED)
- Link/đường dẫn dashboard: submission/evidence/ (local files)
- Kết quả `validate_dashboard.py`: **6/6 panel HOP LE**

## 3. Logging và tracing

- Evidence correlation ID: submission/evidence/log_evidence.txt
- Evidence PII redaction: Submission/evidence/pii_redaction.png (chua co - can them)
- Evidence trace waterfall: submission/evidence/trace_waterfall.png (chua co - can them)
- Giải thích một span đáng chú ý: Due to middleware not being fixed, correlation IDs show as "MISSING". Logs show clear latency patterns: baseline ~150ms, with rag_slow incident ~2650ms.

## 4. Prompt versioning

- Prompt name: day13-chat
- Version/label baseline: v1, labels: baseline, production
- Version/label candidate: v2, label: candidate
- Trace ID của mỗi version: (Langfuse not connected during challenge)
- Bằng chứng đổi label hoặc rollback: submission/evidence/label_change.png (chua co - can them)

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HOP LE: 6/6 panel
- Evidence dashboard: submission/evidence/dashboard_screenshot.png (chua co - can them)
- SLO đã chọn:
  - latency_p95_ms: **2000ms** (K4-specific threshold from challenge.json)
  - error_rate_pct: 2%
  - daily_cost_usd: 2.5
  - quality_score_avg: 0.75
- Alert rules:
  1. P95 latency > 2000ms (K4 threshold)
  2. Error rate > 2%
  3. Quality score < 0.75

## 6. Điều tra challenge

- **Challenge ID**: day13-k4-observability-v1
- **Cohort**: K4
- **Triệu chứng từ metrics**: P95 latency = 2651ms (EXCEEDS 2000ms threshold)
- **Trace ID liên quan**: Tracing not available (Langfuse not connected)
- **Log line/correlation ID liên quan**:
  - Baseline: `latency_ms: 150` at 10:32:18
  - Incident enabled: `event: incident_enabled` at 10:33:27
  - High latency: `latency_ms: 2650-2651` at 10:34:01+
- **Root cause**: rag_slow incident adds `time.sleep(2.5)` in app/mock_rag.py:17-18, causing RAG retrieval to take 2.5 seconds longer
- **Fix action**: Disabled rag_slow incident via `POST /incidents/rag_slow/disable`
- **Preventive measure**:
  1. Add P95 latency alert at 2000ms threshold
  2. Implement RAG timeout monitoring
  3. Add automatic incident detection when P95 > 2000ms

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|------------|-----------|-----------|-------------|
| Member 1 | Logging & PII | aff4f19 | Vietnamese phone PII detection |
| Member 2 | Tracing & Prompt | 4013676 | Langfuse prompt versioning |
| Member 3 | Dashboard & Alerts | 4013676 | 6-panel dashboard setup |
| Member 4 | Challenge Investigation | 5ba6472 | rag_slow root cause analysis |

---

## Evidence Files

| File | Description |
|------|-------------|
| challenge_investigation.md | Full K4 challenge investigation |
| challenge_metrics_before.txt | Baseline metrics (P95: 151ms) |
| challenge_metrics_after.txt | Metrics during incident (P95: 2651ms) |
| log_evidence.txt | Log lines showing latency spike |
| trace_ids_challenge.txt | Challenge investigation summary |

---

## Lab Completion Status

- [x] Checkpoint 0: Setup
- [x] Checkpoint 1: Logging & PII (30/100 - needs correlation ID fix)
- [x] Checkpoint 2: Tracing & Dashboard (6/6 panel validated)
- [x] Checkpoint 3: Challenge (rag_slow investigated, fixed)
- [x] Final: Report completed
