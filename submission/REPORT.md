# Day 13 Observability Report

## 1. Team information

- Cohort: K4
- Challenge ID: `day13-k4-observability-v1`
- Repository URL: `https://github.com/AIVIETNAM-AIO-FalconHeavyX/Day13-K4-Observability-sigmoid`
- Members: Nguyen Hoang Long (`2A202601134`), Nguyen Trong Dang Khoa (`2A202601964`), and Duc Anh (`ducanh2004`).

## 2. Technical results

- `validate_logs.py`: 30/100 estimate; PII detection passed, but existing API logs are missing correlation/enrichment fields.
- Langfuse traces collected: 11 prompt-version traces plus 5 challenge traces.
- PII leaks detected: 0.
- `validate_dashboard.py`: valid, 6/6 panels.
- Dashboard URL: `https://jp.cloud.langfuse.com/project/cmsocubf300bwad0d4tj9avkf`

## 3. Logging and tracing

- Trace evidence: `evidence/trace_waterfall.png`.
- Prompt metadata evidence: `evidence/label_trace_baseline.png` and `evidence/label_trace_candidate.png`.
- Challenge trace `21615682c851a6b8fc7144356dac5b9c` has observation `ab1d35d69a408b91` lasting about 3170ms.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Baseline: version 1, labels `baseline`, `production`
- Candidate: version 2, label `candidate`; added `Answer concisely and professionally.`
- Baseline trace: `1036cd5857573bd6799c3da855a07068`
- Candidate trace: `eaa56ded66e95456619ddea312cc8ce4`
- Production moved to v2: `aab4455e54185f9afb6578a83b899cf2`
- Production rollback to v1: `772428b3f868a93b5b9bce4d9dbb90a6`
- Full trace list: `evidence/trace_ids.txt`
- Evidence: `evidence/prompt_versions.png`, `evidence/rollback_evidence.png`

## 5. Dashboard, SLO and alerts

- Dashboard contract: `validate_dashboard.py` passed with 6/6 panels.
- Dashboard runtime reads `data/logs.jsonl`, refreshes every 30 seconds, and includes latency, traffic, errors, cost, tokens, and quality panels.
- SLO: `latency_p95_ms <= 2000`; this is the strict K4 challenge threshold.
- Dashboard evidence: `evidence/dashboard_screenshot.png`, `evidence/incident_response.png`, `evidence/challenge_dashboard.png`, and `evidence/dashboard_validation.txt`.
- Alerts/runbook: `docs/alerts.md` and `evidence/runbook_example.png`.

## 6. Challenge investigation

- Incident: `rag_slow`
- Symptom: challenge requests measured 4653-4703ms; P50 4657ms and P95/P99 4703ms, all above 2000ms.
- Challenge traces:
  - `21615682c851a6b8fc7144356dac5b9c` (`k4-challenge-s01`)
  - `7476a5ac6e9ea8a29cc8ea9548297163` (`k4-challenge-s02`)
  - `edf8b1dd920dc68b13b4a936e539fd49` (`k4-challenge-s03`)
  - `81361adf2d6794bce5b464166f2cbbfa` (`k4-challenge-s04`)
  - `64e3b7bd497bd2ad55aa4b1be86bc192` (`k4-challenge-s05`)
- Log evidence: `data/logs.jsonl`, response lines 19-27.
- Root cause: `app/mock_rag.py` sleeps for 2.5 seconds whenever `STATE["rag_slow"]` is enabled, directly delaying retrieval.
- Fix: add retrieval timeout, fallback, and cache; remove the blocking delay in production.
- Prevention: instrument retrieval as its own span and alert when P95 exceeds 2000ms.

## 7. Individual contributions

| Member | Work | Commit/Evidence | Lesson |
|---|---|---|---|
| Nguyen Hoang Long (`2A202601134`) | Dashboard panels, K4 SLO, alerts, runbooks, and runtime evidence | `bf1e225` | Connect metrics, traces, and logs using symptom-to-root-cause evidence. |
| Nguyen Trong Dang Khoa (`2A202601964`) | Logging & PII: correlation ID middleware, structured JSON logging, recursive PII redaction, request-context enrichment, and evidence validation | `1494368`, `667f47e` | Protect sensitive data with hashing/redaction and connect logs to traces with correlation IDs. |
| Duc Anh (`ducanh2004`) | Prompt v1/v2, label changes, rollback, trace IDs, and `rag_slow` investigation | `091df7b`; `evidence/trace_ids.txt` and prompt/trace screenshots | Prompt labels enable safe version selection and rollback. |
