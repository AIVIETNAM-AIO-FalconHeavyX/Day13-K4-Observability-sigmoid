# K4 Challenge Investigation Evidence
## Challenge ID: day13-k4-observability-v1
## Cohort: K4
## Date: 2026-08-11

---

## Challenge Configuration

```json
{
  "cohort": "K4",
  "challenge_id": "day13-k4-observability-v1",
  "incident": "rag_slow",
  "affected_feature": "monitoring",
  "latency_threshold_ms": 2000
}
```

---

## Investigation Flow

### Step 1: Baseline Metrics (BEFORE Incident)

```json
{
  "traffic": 5,
  "latency_p50": 150.0,
  "latency_p95": 151.0,
  "latency_p99": 151.0,
  "avg_cost_usd": 0.0019,
  "quality_avg": 0.84
}
```

**Status:** NORMAL - All metrics within acceptable ranges

---

### Step 2: Inject Incident

```bash
curl -X POST http://127.0.0.1:8000/incidents/rag_slow/enable
```

**Response:**
```json
{"ok":true,"incidents":{"rag_slow":true,"tool_fail":false,"cost_spike":false}}
```

---

### Step 3: Symptoms Detected (AFTER Incident)

**Load Test Results:**
```
BEFORE rag_slow: ~150-770ms per request
AFTER rag_slow:  ~10,000-13,000ms per request
```

**Metrics After Incident:**
```json
{
  "traffic": 10,
  "latency_p50": 2650.0,
  "latency_p95": 2651.0,
  "latency_p99": 2651.0,
  "avg_cost_usd": 0.0019,
  "quality_avg": 0.84
}
```

**SYMPTOM:** P95 latency = 2651ms **EXCEEDS K4 THRESHOLD of 2000ms**

---

## Root Cause Analysis

### Evidence from Logs:

```
Timeline:
- 10:32:18 - request_received (baseline traffic)
- 10:32:18 - response_sent with latency_ms: 150 (NORMAL)
- 10:33:27 - incident_enabled (rag_slow)
- 10:34:01 - response_sent with latency_ms: 2650 (SLOW!)
- 10:34:04 - response_sent with latency_ms: 2651 (SLOW!)
```

### Root Cause:

The `rag_slow` incident causes a **2.5 second delay** in RAG retrieval.

**Code Evidence (app/mock_rag.py:17-18):**
```python
if STATE["rag_slow"]:
    time.sleep(2.5)  # Adds 2.5 seconds to every RAG retrieval!
```

**Calculation:**
- Normal latency: ~150ms
- With rag_slow: 150ms + 2500ms = ~2650ms
- **This exceeds the K4 threshold of 2000ms**

---

## Fix Applied

### Action: Disable rag_slow incident

```bash
curl -X POST http://127.0.0.1:8000/incidents/rag_slow/disable
```

**Response:**
```json
{"ok":true,"incidents":{"rag_slow":false,"tool_fail":false,"cost_spike":false}}
```

### Verification:

**After Fix - Load Test Results:**
```
[200] MISSING | monitoring | 158.9ms
[200] MISSING | monitoring | 769.2ms
[200] MISSING | monitoring | 767.7ms
[200] MISSING | monitoring | 767.4ms
[200] MISSING | monitoring | 768.7ms
```

**Status:** RECOVERED - Latency back to normal (~150-770ms)

---

## Preventive Measures

1. **Add P95 latency alert** with threshold at 2000ms (K4-specific)
2. **Implement RAG timeout monitoring** to detect slow retrievals
3. **Add automatic incident detection** when P95 exceeds threshold
4. **Document rag_slow scenario** in runbook for future reference
5. **Consider circuit breaker** for RAG retrieval to prevent cascade failures

---

## Summary

| Metric | Before | After | Threshold | Status |
|--------|--------|-------|-----------|--------|
| P95 Latency | 151ms | 2651ms | 2000ms | EXCEEDED |
| P99 Latency | 151ms | 2651ms | - | HIGH |
| Error Rate | 0% | 0% | 2% | OK |
| Quality | 0.84 | 0.84 | 0.75 | OK |

**Root Cause:** rag_slow incident adds 2.5s delay to RAG retrieval
**Fix:** Disable rag_slow incident
**Recovery:** Latency returned to normal after fix

---

## Files Evidence
- `challenge_metrics_before.txt` - Baseline metrics
- `challenge_metrics_after.txt` - Metrics during incident
- `log_evidence.txt` - Log lines showing latency change
