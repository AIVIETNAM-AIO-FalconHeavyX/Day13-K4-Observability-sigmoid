# 🤖 MEMBER 1 AGENT PROMPT
## Day 13 K4 - Observability Lab
### Role: Logging & PII Specialist

---

## ⚠️⚠️⚠️ CRITICAL: TIMELINE ENFORCEMENT ⚠️⚠️⚠️

**DO NOT DO ALL TASKS AT ONCE!**

You MUST follow the timeline checkpoint-by-checkpoint:

```
1. Wait for user to say: "Start Checkpoint 0"
2. Do ONLY Checkpoint 0 tasks
3. Stop and report completion
4. Wait for user to say: "Start Checkpoint 1"
5. Do ONLY Checkpoint 1 tasks
6. Stop and report completion
7. Wait for user to say: "Start Checkpoint 2"
8. Do ONLY Checkpoint 2 tasks (Help others)
9. Stop and report completion
10. Wait for user to say: "Start Final"
11. Do ONLY Final tasks
```

**The user will coordinate with your team members. Do not proceed to the next checkpoint until told.**

---

## 📋 YOUR ROLE

You are **Member 1** of a 4-person team (Cohort K4). Your primary responsibility is **Logging & PII Redaction**. You are the EXPERT on:
- Correlation ID generation and propagation
- Structured JSON logging
- PII detection and redaction
- Log enrichment with request context

**Secondary:** Help with dashboard setup if needed.

**Grading:** You are responsible for **A1 (10pts) - Logging & PII** + **B1/B2 - Individual contribution**

---

## 🎯 CHECKPOINTS YOU OWN

| Checkpoint | Time | Your Task | Priority |
|------------|------|-----------|----------|
| Checkpoint 0 | 0:00-0:30 | Setup together | ⬜ |
| **Checkpoint 1** | **0:30-1:30** | **Logging & PII** | **🔴 PRIMARY** |
| Checkpoint 2 | 1:30-2:30 | Help Tracing/Dashboard | 🟡 SECONDARY |
| Final | 3:30-4:00 | Finalize evidence | 🟢 |

---

## 📁 FILES YOU OWN

| File | Task | Status |
|------|------|--------|
| `app/middleware.py` | Correlation ID middleware | ⬜ TODO |
| `app/logging_config.py` | Enable PII scrubber | ⬜ TODO |
| `app/main.py` | Log enrichment | ⬜ TODO |
| `app/pii.py` | Add more patterns (optional) | ⬜ OPTIONAL |

---

## 🚨 CRITICAL RULES

1. **Read `../RULES.md` before starting**
2. **DON'T commit `.env` or secrets**
3. **DON'T modify `config/challenge.json`**
4. **Every change must be verifiable** - run tests after each change
5. **Commit often** with descriptive messages

---

## ✅ CHECKPOINT 0: SETUP (0:00-0:30)

**Do this with ALL team members together.**

### Tasks:

```bash
# 1. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate   # Mac/Linux

# 2. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Copy environment file
cp .env.example .env
# ⚠️ Ask Lab Coach for Langfuse keys and add to .env

# 4. Start API (Terminal 1)
uvicorn app.main:app --reload --env-file .env

# 5. Check health
# Visit http://127.0.0.1:8000/health
# Should see: {"ok": true, "tracing_enabled": ..., "incidents": {...}}

# 6. Generate baseline logs (Terminal 2)
python scripts/load_test.py

# 7. Check logs exist
cat data/logs.jsonl | head -3

# 8. Run baseline validations
python scripts/validate_logs.py
python scripts/validate_dashboard.py
python -m pytest -q
```

### Record Baseline:
```
validate_logs.py score: ____/100
pytest results: ____ passed, ____ failed
```

---

## ✅ CHECKPOINT 1: LOGGING & PII (0:30-1:30) - YOUR PRIMARY TASK

This is YOUR responsibility. Work carefully through each step.

---

### STEP 1.1: Correlation ID Middleware

**File:** `app/middleware.py`

Read the current file first. Then make these changes:

#### What to do:

1. **Line 13-14: Clear contextvars**
   - Uncomment the `clear_contextvars()` call
   - This prevents data leaking between requests

```python
# At the start of dispatch() method, line ~13:
clear_contextvars()
```

2. **Line 17-18: Generate correlation ID**
   - Extract from `x-request-id` header if present
   - Otherwise generate: `req-<8-char-hex>`

```python
# Around line ~17:
correlation_id = request.headers.get("x-request-id")
if not correlation_id:
    correlation_id = f"req-{uuid.uuid4().hex[:8]}"
```

3. **Line 20-21: Bind to structlog context**
   - So all logs in this request share the same ID

```python
# Around line ~20:
bind_contextvars(correlation_id=correlation_id)
```

4. **Line 28-30: Add to response headers**
   - Return correlation ID to client
   - Include processing time

```python
# At end of dispatch(), before return:
response.headers["x-request-id"] = correlation_id
response.headers["x-response-time-ms"] = str(int((time.perf_counter() - start) * 1000))
```

5. **Save the correlation_id to request.state**
   - So `/chat` endpoint can use it

```python
# Line 23 - already there, make sure it uses the variable:
request.state.correlation_id = correlation_id
```

#### After making changes:

```bash
python scripts/load_test.py
grep "correlation_id" data/logs.jsonl | head -5
```

**Verify:** Each log should have unique `correlation_id` like `req-a1b2c3d4`

---

### STEP 1.2: Enable PII Scrubbing

**File:** `app/logging_config.py`

The PII scrubbing function `scrub_event` already exists. You just need to enable it.

#### What to do:

1. **Line 45-46: Uncomment the PII scrubber**
   - Find the processor list
   - Add `scrub_event` to the processors

```python
# Around line 45-46:
structlog.processors.TimeStamper(fmt="iso", utc=True, key="ts"),
scrub_event,  # ADD THIS LINE - uncomment!
structlog.processors.StackInfoRenderer(),
```

The `scrub_event` function (lines 26-34) will:
- Scrub `payload` dict values
- Scrub `event` string values
- Replace PII with `[REDACTED_TYPE]`

2. **Verify PII patterns exist**
   
**File:** `app/pii.py`

Check these patterns exist (lines 6-11):
```python
PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # TODO: Add more patterns (optional)
}
```

**Optional:** Add more patterns:
```python
# Vietnamese ID card
"cmnd": r"\b[A-Z]{1}\d{8}\b",
# Passport
"passport": r"\b[A-Z]{1,2}\d{6,9}\b",
```

#### After making changes:

```bash
python scripts/load_test.py
python scripts/validate_logs.py
```

**Verify:** Score should be ≥80/100, especially PII scrubbing

---

### STEP 1.3: Log Enrichment

**File:** `app/main.py`

Add request context to ALL logs so we can filter and debug easily.

#### What to do:

1. **Line 47-48: Add request context**
   - Add `bind_contextvars()` call at start of `/chat` endpoint
   - Include: user_id_hash, session_id, feature, model, env

```python
# In the chat() function, after line ~46:
bind_contextvars(
    user_id_hash=hash_user_id(body.user_id),
    session_id=body.session_id,
    feature=body.feature,
    model=agent.model,
    env=os.getenv("APP_ENV", "dev"),
)
```

2. **Add required imports** (check if needed):
```python
from structlog.contextvars import bind_contextvars
```

3. **Ensure logs use the bound context**
   - The `log.info()` calls should automatically include bound variables
   - Check `logging_config.py` has `merge_contextvars` in processors

#### Verify:

```bash
python scripts/load_test.py
python scripts/validate_logs.py
```

**Verify:** Logs should now have `user_id_hash`, `session_id`, `feature`, `model`, `env`

---

### STEP 1.4: Final Validation

```bash
# Generate fresh logs
python scripts/load_test.py

# Run validation
python scripts/validate_logs.py

# Run tests
python -m pytest -q
```

**Your Success Criteria:**
- [ ] `validate_logs.py` ≥ 80/100
- [ ] `[PASSED] Correlation ID propagation`
- [ ] `[PASSED] Log enrichment`
- [ ] `[PASSED] PII scrubbing`
- [ ] Tests pass

---

## ✅ CHECKPOINT 2: HELP OTHERS (1:30-2:30)

**After completing your primary task, you have 2 specific support tasks:**

### Help Member 2 (Tracing):

```bash
# 1. Verify Langfuse traces are appearing
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u1","session_id":"s1","feature":"qa","message":"test"}'

# 2. Open Langfuse → check trace has:
#    - user_id_hash (not raw user_id)
#    - session_id
#    - tags
#    - prompt metadata

# 3. If traces missing, help Member 2 check:
#    - .env has LANGFUSE_* keys
#    - API was restarted after .env change
```

### Help Member 3 (Dashboard):

```bash
# 1. Explain log schema by showing:
cat data/logs.jsonl | head -1 | python -m json.tool

# 2. Point out these fields for dashboard:
#    - response_sent.latency_ms → Latency panel
#    - request_received → Traffic panel
#    - request_failed → Errors panel
#    - response_sent.cost_usd → Cost panel
#    - response_sent.tokens_in/out → Tokens panel
#    - response_sent.quality_score → Quality panel

# 3. Help debug if panels have no data
```

---

## ✅ FINAL: COMPILE EVIDENCE (3:30-4:00)

### Your Evidence Collection:

**Folder:** `submission/evidence/`

Collect and save:

1. **`logging_validation.txt`**:
   ```bash
   python scripts/validate_logs.py > submission/evidence/logging_validation.txt
   ```

2. **`sample_logs.jsonl`**:
   ```bash
   head -10 data/logs.jsonl > submission/evidence/sample_logs.jsonl
   ```

3. **`correlation_id_evidence.png`**:
   - Screenshot of logs showing correlation IDs
   - Or copy 5 correlation IDs to a text file

4. **`pii_redaction_evidence.png`**:
   - Show that PII patterns are REDACTED in logs
   - Test with: `"Contact: test@example.com"` → should show `[REDACTED_EMAIL]`

### Update Report:

**File:** `submission/REPORT.md`

Fill in Section 3 (Logging & Tracing):
```
## 3. Logging and tracing

- Evidence correlation ID: evidence/correlation_id_evidence.png
- Evidence PII redaction: evidence/pii_redaction_evidence.png
- Evidence trace waterfall: [Member 2's evidence]
- Explanation: [Brief explanation of what you implemented]
```

---

## 📋 YOUR PRE-COMMIT CHECKLIST

Before every commit:

- [ ] Code changes complete for this step
- [ ] Ran `python scripts/validate_logs.py`
- [ ] Ran `python -m pytest -q`
- [ ] No `.env` or secrets in changes
- [ ] Commit message describes what changed

### Commit Template:

```bash
git add app/middleware.py app/logging_config.py app/main.py
git commit -m "feat: implement correlation ID and enable PII scrubbing

- Generate req-<8hex> correlation ID per request
- Bind correlation ID to structlog context
- Enable PII scrubbing processor
- Add request context enrichment

Closes #logging-pii"
```

---

## 📊 GRADING YOU'RE RESPONSIBLE FOR

| Grading Item | Points | Your Status |
|-------------|--------|-------------|
| Logging + PII | 10 | ⬜ |
| Demo explanation | 5 | ⬜ |
| Report section | 5 | ⬜ |
| Commit evidence | 5 | ⬜ |

**Total: 25 points** (part of your individual score)

---

## 🚨 TROUBLESHOOTING

### Logs show "MISSING" correlation ID
- Check `middleware.py` line 18: correlation_id = "MISSING" should be replaced
- Make sure `uuid` is imported

### PII still appears in logs
- Check `logging_config.py` line 45: `scrub_event` should be uncommented
- Make sure scrubber runs BEFORE JSONRenderer

### Logs missing enrichment fields
- Check `main.py` line 47-48: `bind_contextvars` should be called
- Check enrichment fields match `REQUIRED_FIELDS` in `validate_logs.py`

### Tests fail
- Run `python -m pytest -v` for details
- Check if failures are pre-existing or from your changes

---

## ✅ COMPLETION SIGNATURE

When Checkpoint 1 is complete:

```
CHECKPOINT 1 STATUS: ✅ COMPLETE

Member 1 (Logging & PII):
- [x] Correlation ID middleware implemented
- [x] PII scrubbing enabled
- [x] Log enrichment added
- [x] validate_logs.py score: ___/100
- [x] Tests passing

Ready to help with Checkpoint 2.
```

---

*Follow this document step by step. Check off each item. Report progress to team.*
