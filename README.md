# 📬 Email Assistant

An AI assistant that triages your inbox and drafts replies **in your own voice** —
built live on stage with Claude Code (BWCC Cohort 003, Week 1).

Everything runs **locally**. Your emails never leave your machine: the voice
profile is local embeddings, and drafting/classification run through Claude Code.

---

## What it does

| Milestone | What it does | How |
|---|---|---|
| **M1 — Voice** | Learns how *you* write | Embeds your sent emails into a local vector store; retrieves your most similar past replies for any new email |
| **M2 — Triage** | Sorts inbound mail into *your* categories | A Claude Code classifier agent tags each email with category + urgency + suggested action + confidence |
| **M3 — Draft** | Writes + reviews replies | A drafter agent writes a reply grounded in your voice examples; a reviewer agent checks it; a Streamlit dashboard shows it all |

---

## Quick start

```bash
# 1. Set up a virtual environment + install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. (One time) Pull your sent emails into a voice corpus
#    Needs Gmail OAuth — see "Gmail setup" below.
python m1-voice/extract_emails.py        # -> data/raw_emails.jsonl

# 3. M1 — build the voice profile and try it
python m1-voice/build_embeddings.py      # -> data/embeddings.db
python m1-voice/retrieve.py < data/sample_inbound.txt

# 4. M2 — classify your inbound emails
python m2-classifier/classify.py         # -> data/classified.json

# 5. M3 — draft + review, then open the dashboard
python m3-dashboard/orchestrate.py       # -> data/drafts.json
streamlit run m3-dashboard/app.py
```

**One-line "everything's running" demo** (after deps + corpus exist):

```bash
python m1-voice/build_embeddings.py && python m2-classifier/classify.py && \
python m3-dashboard/orchestrate.py && streamlit run m3-dashboard/app.py
```

---

## Gmail setup (for `extract_emails.py`)

1. In [Google Cloud Console](https://console.cloud.google.com/): create a project,
   enable the **Gmail API**, create an **OAuth client ID** (type: *Desktop app*).
2. Download the client secret JSON to `data/auth/credentials.json`.
3. Run `python m1-voice/extract_emails.py` — a browser opens for one-time consent.
   The token is cached to `data/auth/token.json` (both are gitignored).

> The repo ships with `data/raw_emails.jsonl` already populated, so you can run
> M1–M3 without doing this. Re-run only to refresh from your live inbox.

---

## Configuration

Copy `.env.example` to `.env` and adjust. Key knobs:

- `EMBED_MODEL` — the local embedding model (default `all-MiniLM-L6-v2`)
- `RETRIEVE_K` — how many past replies to retrieve (the live "top-K" knob)
- `CLASSIFY_MODEL` / `DRAFT_MODEL` — which Claude model the agents use

---

## Project layout

```
.claude/agents/        classifier · drafter · reviewer  (editable prompts)
m1-voice/              extract_emails · build_embeddings · retrieve
m2-classifier/         classify · schema · categories.yaml
m3-dashboard/          app (Streamlit) · orchestrate
data/                  corpus, vector db, classified.json, drafts.json
giveaways/             3 standalone starter kits (see each README)
```

## Notes & safety

- **Nothing is sent.** The dashboard's Send/Edit/Skip buttons are display-only.
- Embeddings are **retrieval, not training** — your emails fine-tune nothing.
- Secrets (`data/auth/`, `.env`) are gitignored. Don't commit them.
