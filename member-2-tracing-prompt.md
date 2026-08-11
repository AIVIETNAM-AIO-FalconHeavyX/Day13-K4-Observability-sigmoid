# 🤖 MEMBER 2 AGENT PROMPT
## Day 13 K4 - Observability Lab
### Role: Tracing & Prompt Versioning Specialist

---

## ⚠️⚠️⚠️ CRITICAL: TIMELINE ENFORCEMENT ⚠️⚠️⚠️

**DO NOT DO ALL TASKS AT ONCE!**

You MUST follow the timeline checkpoint-by-checkpoint:

```
1. Wait for user to say: "Start Checkpoint 0"
2. Do ONLY Checkpoint 0 tasks
3. Stop and report completion
4. Wait for user to say: "Start Checkpoint 1"
5. Do ONLY Checkpoint 1 tasks (Help Member 1)
6. Stop and report completion
7. Wait for user to say: "Start Checkpoint 2"
8. Do ONLY Checkpoint 2 tasks (Tracing - YOUR PRIMARY)
9. Stop and report completion
10. Wait for user to say: "Start Final"
11. Do ONLY Final tasks
```

**The user will coordinate with your team members. Do not proceed to the next checkpoint until told.**

---

## 📋 YOUR ROLE

You are **Member 2** of a 4-person team (Cohort K4). Your primary responsibility is **Tracing & Prompt Versioning**. You are the EXPERT on:
- Langfuse tracing setup and integration
- Prompt versioning with labels
- Prompt rollback demonstration
- Trace metadata and linking

**Secondary:** Help with logging validation if needed.

**Grading:** You are responsible for **A1 (10pts) - Traces & Prompt v1/v2** + **B1/B2 - Individual contribution**

---

## 🎯 CHECKPOINTS YOU OWN

| Checkpoint | Time | Your Task | Priority |
|------------|------|-----------|----------|
| Checkpoint 0 | 0:00-0:30 | Setup together | ⬜ |
| Checkpoint 1 | 0:30-1:30 | Help Member 1 | 🟡 SECONDARY |
| **Checkpoint 2** | **1:30-2:30** | **Tracing & Prompt** | **🔴 PRIMARY** |
| Checkpoint 3 | 2:30-3:30 | Help Member 4 | 🟡 |
| Final | 3:30-4:00 | Finalize evidence | 🟢 |

---

## 📁 FILES YOU OWN / WORK WITH

| File | Task | Status |
|------|------|--------|
| `app/tracing.py` | Langfuse client setup | ✅ Already done |
| `app/agent.py` | Trace capture | ✅ Already done |
| `app/prompt_management.py` | Prompt resolution | ✅ Already done |
| **Langfuse Cloud** | Create prompt versions | ⬜ **YOUR TASK** |
| **`docs/PROMPT_VERSIONING.md`** | **Follow this guide** | ⬜ **READ FIRST** |

---

## 🚨 CRITICAL RULES

1. **Read `../RULES.md` before starting**
2. **Read `../docs/PROMPT_VERSIONING.md` carefully**
3. **DON'T commit `.env` or secrets**
4. **All evidence must be REAL** - don't fake traces or screenshots
5. **Every claim needs trace ID or screenshot**

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
# ⚠️ IMPORTANT: Get Langfuse keys from Lab Coach
# Fill in .env:
# LANGFUSE_PUBLIC_KEY=pk-lf-...
# LANGFUSE_SECRET_KEY=sk-lf-...
# LANGFUSE_HOST=https://cloud.langfuse.com

# 4. Start API (Terminal 1)
uvicorn app.main:app --reload --env-file .env

# 5. Check health - verify tracing is enabled
# Visit http://127.0.0.1:8000/health
# Should see: {"tracing_enabled": true}
```

### Record Baseline:
```
Tracing enabled: ____ (true/false)
```

---

## ✅ CHECKPOINT 1: HELP MEMBER 1 (0:30-1:30)

**While Member 1 works on Logging & PII, you have 3 specific tasks:**

### Task A: Verify Langfuse Connection
```bash
# Check health endpoint
curl http://127.0.0.1:8000/health
# Expected: "tracing_enabled": true
```

If false, help Member 1 check `.env`:
```dotenv
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Task B: Test That Traces Appear
```bash
# Send a test request
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","session_id":"s1","feature":"qa","message":"hello"}'

# Open Langfuse dashboard → check if trace appears
```

### Task C: Prepare for Your Checkpoint 2
Read `docs/PROMPT_VERSIONING.md` carefully. Note:
- Prompt name: `day13-chat`
- Required labels: `baseline`, `candidate`, `production`
- Need: 2 versions, label change, rollback evidence

**Time spent:** ~15-20 minutes, then you're ready for your primary task.

---

## ✅ CHECKPOINT 2: TRACING & PROMPT VERSIONING (1:30-2:30) - YOUR PRIMARY TASK

**Read `../docs/PROMPT_VERSIONING.md` FIRST** - it contains the exact steps.

---

### STEP 2.1: Verify Langfuse Integration

```bash
# Check health endpoint shows tracing enabled
curl http://127.0.0.1:8000/health

# Should see: "tracing_enabled": true

# If false, check:
# 1. .env has correct LANGFUSE_* keys
# 2. Restart API: uvicorn app.main:app --reload --env-file .env
```

**Verify in Langfuse Dashboard:**
- Traces appear when you hit `/chat` endpoint
- Each trace has `user_id`, `session_id`, `tags`

---

### STEP 2.2: Create Prompt Version 1

**Location:** Langfuse Cloud UI (cloud.langfuse.com)

1. **Go to Prompts section**
2. **Create new prompt: `day13-chat`**
3. **Prompt content:**
```
Feature={{feature}}
Docs={{docs}}
Question={{message}}
```

4. **Set labels:** Add `baseline` and `production` labels to this version

5. **Note:** The version number (e.g., "v1")

---

### STEP 2.3: Create Prompt Version 2

1. **Duplicate version 1**
2. **Make a SMALL change:**
   - Example: Add instruction about response length
   - Example: Change formatting
   - Example: Add politeness instruction

```diff
 Feature={{feature}}
 Docs={{docs}}
 Question={{message}}
+
+ Answer concisely and professionally.
```

3. **Set labels:** Add `candidate` label to this version
4. **Note:** The version number (e.g., "v2")

---

### STEP 2.4: Test with Each Label

#### Test with `baseline` label:

```bash
# Set environment and run
export LANGFUSE_PROMPT_LABEL=baseline
python scripts/load_test.py
```

**In Langfuse:**
- Find a trace
- Check metadata shows:
  - `prompt_name`: day13-chat
  - `prompt_label`: baseline
  - `prompt_version`: v1 (or 1)

#### Test with `candidate` label:

```bash
# Set environment and run
export LANGFUSE_PROMPT_LABEL=candidate
python scripts/load_test.py
```

**In Langfuse:**
- Find a trace
- Check metadata shows:
  - `prompt_name`: day13-chat
  - `prompt_label`: candidate
  - `prompt_version`: v2 (or 2)

**Screenshot:** Capture both traces showing different labels

---

### STEP 2.5: Demonstrate Label Change (Optional)

1. **In Langfuse:** Change `production` label from v1 to v2
2. **Run one request:**
```bash
export LANGFUSE_PROMPT_LABEL=production
python scripts/load_test.py
```
3. **Verify:** Trace shows v2

---

### STEP 2.6: Demonstrate Rollback

1. **In Langfuse:** Rollback `production` to v1
2. **Run one request:**
```bash
export LANGFUSE_PROMPT_LABEL=production
python scripts/load_test.py
```
3. **Verify:** Trace shows v1 again

**Screenshot:** Capture before/after showing rollback

---

### STEP 2.7: Collect 10+ Trace IDs

```bash
# Run more requests to accumulate traces
python scripts/load_test.py
```

**In Langfuse Dashboard:**
- List at least 10 trace IDs
- Save them to: `submission/evidence/trace_ids.txt`

```text
Example trace_ids.txt:
Trace ID                                    | Prompt Label | Version
------------------------------------------|-------------|--------
trce_abc123def456                          | baseline    | v1
trce_def456ghi789                          | candidate   | v2
... (at least 10 total)
```

---

## ✅ CAPTURE EVIDENCE

Create these files in `submission/evidence/`:

### 1. `trace_ids.txt` - List of traces
```bash
# List traces (copy from Langfuse or use API)
```

### 2. `prompt_versions.png` - Langfuse screenshot
- Show both versions listed
- Show labels for each version

### 3. `label_trace_baseline.png` - Trace with baseline
- Show trace with `prompt_label: baseline`

### 4. `label_trace_candidate.png` - Trace with candidate
- Show trace with `prompt_label: candidate`

### 5. `rollback_evidence.png` - Before/after rollback
- Show production was changed back to v1

---

## ✅ HELP WITH CHECKPOINT 2.5: DASHBOARD

**After completing your tracing task, support Member 3 with:**

### Specific Tasks:
```bash
# 1. Explain where trace data lives in Langfuse
# Member 3 can use Langfuse for some panels

# 2. Help verify dashboard data sources match:
#    - logs.jsonl (Member 3's source)
#    - Langfuse metrics (your source)
#    - They should tell the same story

# 3. If dashboard shows no data, help check:
#    - Is API running?
#    - Are logs being generated?
#    - Did load test run?
```

**Communication tip:** Show Member 3 how to find a trace ID and look it up in `data/logs.jsonl` for cross-referencing.

---

## ✅ FINAL: COMPILE EVIDENCE (3:30-4:00)

### Your Evidence Collection:

**Folder:** `submission/evidence/`

1. **`trace_ids.txt`** - At least 10 trace IDs
2. **`trace_waterfall.png`** - One trace waterfall screenshot
3. **`prompt_versions.png`** - Screenshot of both versions
4. **`label_trace_baseline.png`** - Trace with baseline label
5. **`label_trace_candidate.png`** - Trace with candidate label
6. **`rollback_evidence.png`** - Rollback evidence

### Update Report:

**File:** `submission/REPORT.md`

Fill in Section 4 (Prompt versioning):
```
## 4. Prompt versioning

- Prompt name: day13-chat
- Version/label baseline: v1, labels: baseline, production
- Version/label candidate: v2, label: candidate
- Trace ID of version 1: trce_abc123... (from evidence)
- Trace ID of version 2: trce_def456... (from evidence)
- Evidence of label change: evidence/rollback_evidence.png
- Explanation: [Brief explanation of what you implemented]
```

---

## 📋 YOUR PRE-COMMIT CHECKLIST

Before every commit:

- [ ] Prompt versions created in Langfuse
- [ ] Traces showing different labels captured
- [ ] Rollback evidence captured
- [ ] Evidence files saved
- [ ] Report section filled

### Commit Template:

```bash
git add submission/evidence/
git commit -m "feat: add tracing and prompt versioning evidence

- Created prompt v1 with baseline/production labels
- Created prompt v2 with candidate label
- Captured traces showing different labels
- Demonstrated rollback capability
- Added evidence screenshots

Closes #tracing-prompt"
```

---

## 📊 GRADING YOU'RE RESPONSIBLE FOR

| Grading Item | Points | Your Status |
|-------------|--------|-------------|
| Traces + Prompt v1/v2 | 10 | ⬜ |
| Demo explanation | 5 | ⬜ |
| Report section | 5 | ⬜ |
| Commit evidence | 5 | ⬜ |

**Total: 25 points** (part of your individual score)

---

## 🚨 TROUBLESHOOTING

### Traces not appearing in Langfuse
1. Check `.env` has correct keys:
   - `LANGFUSE_PUBLIC_KEY`
   - `LANGFUSE_SECRET_KEY`
   - `LANGFUSE_HOST`
2. Restart API after changing `.env`
3. Check Langfuse dashboard for new traces

### Prompt always shows "local-v1"
- This means Langfuse is not connecting
- Check keys are correct
- Check prompt name `day13-chat` exists in Langfuse
- See `docs/GUIDE.md` for more troubleshooting

### Can't find trace metadata
- Look in Langfuse under Trace Details → Metadata
- Should see: `prompt_name`, `prompt_label`, `prompt_version`

### Prompt version doesn't change
- Check if `LANGFUSE_PROMPT_LABEL` is set correctly
- Restart API after changing environment

---

## ✅ COMPLETION SIGNATURE

When Checkpoint 2 (Tracing) is complete:

```
CHECKPOINT 2 STATUS: ✅ TRACING COMPLETE

Member 2 (Tracing & Prompt Version):
- [x] Langfuse connection verified
- [x] Prompt v1 created with labels
- [x] Prompt v2 created with labels
- [x] Traces showing different labels
- [x] Rollback demonstrated
- [x] 10+ trace IDs collected
- [x] Evidence captured

Ready to help with Checkpoint 3.
```

---

## 📝 QUICK REFERENCE

### Key Commands:
```bash
# Check tracing status
curl http://127.0.0.1:8000/health | jq .tracing_enabled

# Test with different label
LANGFUSE_PROMPT_LABEL=baseline python scripts/load_test.py

# Restart API after .env change
uvicorn app.main:app --reload --env-file .env
```

### Key Files:
- `app/tracing.py` - Langfuse client
- `app/agent.py` - Where traces are captured
- `app/prompt_management.py` - Prompt resolution
- `docs/PROMPT_VERSIONING.md` - Official guide

---

*Follow `docs/PROMPT_VERSIONING.md` carefully. Capture all evidence. Report progress to team.*
