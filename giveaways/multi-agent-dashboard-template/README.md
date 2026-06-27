# 📬 Multi-Agent Dashboard Template

A polished **v0.1 starter kit** showing a two-agent loop (**drafter → reviewer**)
wired to a clean **Streamlit dashboard**. Drop in a list of pre-classified
emails, run the agent loop to draft + review replies, and view everything in a
dark, screen-share-friendly UI.

It ships with ~6 synthetic emails so it renders the moment you clone it — no
data, no API keys, no embeddings.

```
streamlit run app.py
```

---

## What's inside

| File | What it does |
| --- | --- |
| `app.py` | Streamlit dashboard. Per email: category + urgency tags, drafted reply, reviewer verdict side-by-side, display-only Send/Edit/Skip, Refresh. |
| `orchestrate.py` | The multi-agent loop. Runs **drafter → reviewer** for each email in parallel (ThreadPoolExecutor), via the `claude` CLI, and writes `drafts.json`. |
| `.claude/agents/drafter.md` | Drafter agent prompt — writes a reply in the user's voice. |
| `.claude/agents/reviewer.md` | Reviewer agent prompt — returns a JSON verdict (`approve` / `revise`). |
| `examples/sample_emails.json` | ~6 **synthetic** pre-classified emails, with inline voice examples. |
| `components/` | Placeholder for Streamlit fragment components as the UI grows. |
| `deploy.sh` | Local-only: makes a venv, installs deps, launches the dashboard. |

---

## Prerequisites

- **Python 3.11+**
- **[Claude Code](https://docs.claude.com/en/docs/claude-code) (`claude` CLI)** — only needed to *generate* drafts with `orchestrate.py`. The dashboard alone runs without it.

Check you have both:

```bash
python3 --version   # 3.11 or higher
claude --version    # any recent version
```

---

## Setup (under 5 minutes)

```bash
# 1. Clone, then enter the template
cd multi-agent-dashboard-template

# 2. Create + activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies (just streamlit + python-dotenv)
pip install -r requirements.txt

# 4. Run the dashboard — it renders the bundled synthetic emails immediately
streamlit run app.py
```

Open http://localhost:8501. You'll see the inbox triaged with tags. Cards show
"No draft yet" until you run the agent loop.

> Shortcut: `./deploy.sh` does steps 2-4 for you.

---

## Generate drafts with the multi-agent loop

With the `claude` CLI installed:

```bash
python orchestrate.py
```

This runs **drafter → reviewer** for each email concurrently and writes
`drafts.json`. Refresh the dashboard (🔄 button) and each card now shows the
drafted reply plus the reviewer's `APPROVE` / `REVISE` verdict.

The loop calls the model `claude-haiku-4-5-20251001` by default.

### Use your own emails

`app.py` and `orchestrate.py` look for `classified.json` first, then fall back to
`examples/sample_emails.json`. To use your own inbox, create a `classified.json`
at the repo root (same shape as the sample) and point the loop at it:

```bash
EMAILS_JSON=classified.json python orchestrate.py
```

Each email is an object:

```json
{
  "id": "e1",
  "sender": "Name <name@example.com>",
  "subject": "...",
  "snippet": "the email body / preview",
  "category": "pricing_inquiry",
  "urgency": "high",
  "voice_examples": ["a past reply in your voice", "another one"]
}
```

`voice_examples` is **optional** — it's how the drafter grounds the reply in
your tone. Omit it and the drafter falls back to a sensible default voice. (This
template has **no embeddings dependency**; voice examples are passed inline
rather than retrieved.)

### Environment overrides

Set these in your shell or a `.env` file:

| Variable | Default | Purpose |
| --- | --- | --- |
| `EMAILS_JSON` | `examples/sample_emails.json` | Input emails for the loop |
| `DRAFTS_JSON` | `drafts.json` | Where the loop writes results |
| `DRAFT_MODEL` | `claude-haiku-4-5-20251001` | Model for both agents |
| `ORCHESTRATE_WORKERS` | `8` | Parallel drafter→reviewer chains |

---

## Notes

- **The Send / Edit / Skip buttons are display-only** — no email is ever sent.
- All bundled data is **synthetic**. No real inbox is included.

**Local-only. Cohort weeks 3-4 teach auth, persistence, monitoring.**

See [`extension-notes.md`](./extension-notes.md) for where to take this next.
