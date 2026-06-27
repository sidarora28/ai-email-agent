# 🎬 Live build cheat-sheet (this is the `live-start` branch)

This branch is the **70%-built starting point** for the masterclass. The code is
all here; the ~30% you complete on stage is withheld:

- `m2-classifier/categories.yaml` → empty (you fill it)
- `.claude/agents/classifier.md` → rough first pass (you tighten it)
- `.claude/agents/drafter.md` + `reviewer.md` → placeholders (you teach the voice)
- `data/embeddings.db` → empty (you build it live)
- no `classified.json` / `drafts.json` yet (you generate them live)

> **Failsafe:** keep a second IDE window open on the `failsafe` branch (the fully
> built version). If anything breaks: *"while that recovers, here's what it looks
> like fully running"* → cut to that window.

---

## Run of show

### M1 — Voice profile (~27 min)
```bash
python m1-voice/build_embeddings.py            # watch it embed your sent emails
python m1-voice/retrieve.py < data/sample_inbound.txt   # "sounds like me"
# tweak: change RETRIEVE_K from 5 to 3, re-run, show the effect
```

### M2 — Classification (~24 min)
1. Fill `m2-classifier/categories.yaml` live (5–6 of YOUR categories).
2. Edit `.claude/agents/classifier.md` once (wrong → tweak → right).
```bash
python m2-classifier/classify.py               # real-time classification
```

### M3 — Multi-agent + dashboard (~28 min)
1. Edit `.claude/agents/drafter.md` + `reviewer.md` live (teach the voice).
```bash
python m3-dashboard/orchestrate.py             # watch drafter -> reviewer
streamlit run m3-dashboard/app.py              # the dashboard
```
2. Ask Claude Code live: *"improve the dashboard styling so [X]"* → app.py edits.
3. Final: hit **Refresh** to pull a real unread email through the whole flow.

---

## Pre-flight (do before going on stage)
- [ ] `pip install -r requirements.txt` done in `.venv`
- [ ] `data/raw_emails.jsonl` present (your corpus)
- [ ] `data/sample_inbound.txt` present
- [ ] `claude` CLI logged in
- [ ] Second window open on `failsafe`, dashboard already running there
- [ ] `DEMO_MASK=1` (default) so contacts are masked on screen
