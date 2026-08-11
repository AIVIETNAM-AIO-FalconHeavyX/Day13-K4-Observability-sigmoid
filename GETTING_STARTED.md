# 🚀 Team Getting Started Guide
## Day 13 K4 - Observability Lab

---

## 🚨 IMPORTANT: K4 CHALLENGE ALREADY RELEASED!

```
config/challenge.json contains:
- Cohort: K4
- Challenge ID: day13-k4-observability-v1
- Incident: rag_slow
- Affected Feature: monitoring
- Latency Threshold: 2000ms (STRICTER!)
```

---

## 📋 QUICK OVERVIEW

| Role | Your File | Your Primary Task |
|------|-----------|------------------|
| Member 1 | `member-1-logging-pii.md` | Correlation ID + PII + Logging |
| Member 2 | `member-2-tracing-prompt.md` | Langfuse traces + Prompt versioning |
| Member 3 | `member-3-dashboard-alerts.md` | Dashboard + SLO (2000ms!) + Alerts |
| Member 4 | `member-4-incident-report.md` | Challenge investigation (rag_slow) + Report |

---

## 📁 STEP 1: Get Your Agent File

**Option A: Copy from teammate**

1. Member 1 shares `member-1-logging-pii.md` with Member 1
2. Member 2 shares `member-2-tracing-prompt.md` with Member 2
3. etc.

**Option B: Copy-paste**

Open each file in the repo, copy all content, send to the respective member.

---

## 💻 STEP 2: Start Your Agent Session

### ⚠️ IMPORTANT: Do NOT Let Agent Do Everything At Once!

**The agent file contains ALL checkpoints. You must control the timeline.**

### How It Works:

```
1. Paste agent file content
2. Agent waits for your signal
3. You say: "Start Checkpoint 0"
4. Agent does ONLY Checkpoint 0
5. Agent reports: "Done with Checkpoint 0"
6. You say: "Start Checkpoint 1"
7. Agent does ONLY Checkpoint 1
8. Repeat...
```

### Example Prompts to Agent:

```
Checkpoint 0:  "Start Checkpoint 0. Setup the environment together."
Checkpoint 1:  "We're at 0:30. Start Checkpoint 1 - Logging & PII."
Checkpoint 2:  "We're at 1:30. Start Checkpoint 2 - Tracing & Dashboard."
Checkpoint 3:  "Start Checkpoint 3 - Challenge investigation (rag_slow)."
Final:         "We're at 3:30. Start Final - Report & Submit."
```

---

## ⏰ STEP 3: Your Checkpoint Timeline

**Your personal timeline (follow when the team signals):**

```
⏱️ TIME    | CHECKPOINT | WHAT YOU DO
-----------|------------|-----------------------------------------
0:00-0:30  | Checkpoint 0 | Setup together (all members)
0:30-1:30  | Checkpoint 1 | YOUR PRIMARY TASK (Logging & PII)
1:30-2:30  | Checkpoint 2 | Tracing + Dashboard (Members 2 & 3)
2:30-3:30  | Checkpoint 3 | Challenge: rag_slow (Member 4)
3:30-4:00  | Final       | Report & Submit
```

---

## 🚨 K4-SPECIFIC NOTES

### Latency Threshold
- **Default lab:** 3000ms
- **K4 Challenge:** **2000ms** (stricter!)

### Challenge Incident
- **K4 uses:** `rag_slow`
- **Affected feature:** `monitoring`

### Queries
- K4 has 5 specific queries with K4 prefixes (k4-u01, k4-u02, etc.)

---

## 👥 STEP 4: Coordinate via GitHub

### Setup (Do once):

```bash
# Clone your own fork
git clone https://github.com/YOUR_USERNAME/Day13-K4-Observability-sigmoid.git
```

### During Lab:

```bash
# When you finish your task
git add app/ config/ docs/
git commit -m "feat: [what you did]"
git push origin main
```

---

## 📊 STEP 5: Validation Commands

**Run these often:**

```bash
# 1. Check tests
python -m pytest -q

# 2. Validate logs
python scripts/validate_logs.py

# 3. Validate dashboard
python scripts/validate_dashboard.py

# 4. Check for secrets
git status --short
```

---

## 🎯 STEP 6: Checkpoints Overview

### Checkpoint 0: Setup (0:00-0:30)
- [ ] Python venv created
- [ ] Dependencies installed
- [ ] API running at http://127.0.0.1:8000
- [ ] `/health` returns `{"ok": true}`
- [ ] `data/logs.jsonl` exists

### Checkpoint 1: Logging & PII (0:30-1:30)
- [ ] Correlation IDs in logs
- [ ] PII redacted
- [ ] Log enrichment working
- [ ] `validate_logs.py` ≥ 80/100

### Checkpoint 2: Tracing & Dashboard (1:30-2:30)
- [ ] ≥10 traces in Langfuse
- [ ] Prompt v1 + v2 created
- [ ] Label change shown
- [ ] Dashboard: 6/6 panels
- [ ] **`validate_dashboard.py` passes**
- [ ] SLO: **2000ms for K4!**

### Checkpoint 3: Challenge (2:30-3:30)
- [ ] Incident: **rag_slow**
- [ ] Affected feature: **monitoring**
- [ ] Latency threshold: **2000ms**
- [ ] Root cause found
- [ ] Fix applied
- [ ] Investigation documented

### Final: Report (3:30-4:00)
- [ ] `submission/REPORT.md` complete
- [ ] Evidence collected
- [ ] All tests passing
- [ ] Pushed to GitHub
- [ ] Submitted

---

## 🆘 TROUBLESHOOTING

### "I don't know what to do"
→ Read your agent file from the top. Follow the steps.

### "My agent is stuck"
→ Stop and restart. Paste the file content again.

### "K4 Latency Threshold"
→ Remember: **2000ms**, not 3000ms!

### "Challenge not working"
→ K4 challenge is already released. Just run:
```bash
python scripts/inject_incident.py
python scripts/load_test.py --challenge --concurrency 5
```

---

## 📞 COMMUNICATION TEMPLATE

When coordinating with team:

```
STATUS UPDATE (K4):
━━━━━━━━━━━━━━━
✅ Checkpoint 0: DONE
🔄 Checkpoint 1: Member 1 working (70% done)
⬜ Checkpoint 2: Waiting
⬜ Checkpoint 3: Waiting (rag_slow incident)

ISSUES:
━━━━━━━━━━━━━━━
- None currently

K4 REMINDERS:
━━━━━━━━━━━━━━━
- Latency threshold: 2000ms
- Challenge incident: rag_slow
- Affected feature: monitoring
```

---

## ✅ FINAL CHECKLIST

Before saying "I'm done":

- [ ] Ran `python -m pytest -q` → all tests pass
- [ ] Ran `python scripts/validate_logs.py` → ≥80/100
- [ ] Ran `python scripts/validate_dashboard.py` → 6/6
- [ ] No `.env` or secrets in my commits
- [ ] Evidence captured in `submission/evidence/`
- [ ] `submission/REPORT.md` section filled
- [ ] **K4 threshold is 2000ms!**
- [ ] Told team: "I'm done with [my task]"

---

## 🚀 READY? LET'S BEGIN!

```
1. Get your agent file
2. Open Claude Code / your AI assistant
3. Paste your agent file content
4. Follow the instructions
5. Communicate with team
6. Submit!

GOAL: Complete K4 Challenge (rag_slow, 2000ms threshold)
```
