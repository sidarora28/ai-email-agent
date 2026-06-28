# 🎬 Run of Show — Email Assistant masterclass

Everything is pre-built and works. On stage you **run pre-tested commands** and make
a couple of small live edits. A second terminal stays on `main` (fully working) as
your failsafe — if anything wobbles, switch to it and keep talking.

> Before you start: `source .venv/bin/activate` in your terminal.

---

## ACT 1 — Cold open: the finished product (~8 min)
Show it working on your real inbox first. Narrate each step.

```bash
bash fetch-emails.sh        # "it pulls my unread inbox"
bash categorize-emails.sh   # "it sorts them into MY categories — not generic ones"
bash write-replies.sh       # "watch it draft in my voice — and a 2nd agent review it"
```

Then to the audience: **"email me right now."** Wait ~30s:
```bash
bash fetch-emails.sh        # their emails appear
bash categorize-emails.sh
bash write-replies.sh       # drafted live, in your voice
```

---

## ACT 2 — Slides (~8 min)
- What it is · the 3 concepts (voice via embeddings · custom classification · writer+reviewer)
- Scope: what we build live vs. what the cohort teaches.

---

## ACT 3 — The live build (~60 min)
Reset to the "70% built" start, then build the magic live.

```bash
bash reset-for-demo.sh      # keeps the slow pre-built bits; clears what we make live
```

### M1 — Voice (~25 min)  → drop **Voice kit** at ~min 22
```bash
python m1_voice/learn_voice.py        # watch Opus discover your 7 categories + write your voice profile
cat data/voice_profile.md             # read a section aloud: "yep, that's how I write"
python m1_voice/build_voice_index.py  # the index the reviewer uses
```

### M2 — Classify (~24 min)  → drop **Classifier kit** at ~min 50
- Open `m2_classify/handling.yaml`, add or tweak one category live.
```bash
bash categorize-emails.sh             # watch routing: draft / → Sid / skip
```

### M3 — Writer + Reviewer (~28 min)  → drop **Dashboard kit** at ~min 75
- Open `.claude/agents/drafter.md`, tweak one line live (e.g. tighten the voice).
```bash
bash write-replies.sh                 # WRITER streams the reply, REVIEWER checks it
```
- Finale: pull a real unread email through the whole flow (`fetch → categorize → write`).

---

## Failsafes
- **Usage limit / Claude error:** `write-replies.sh` auto-falls back to the last good
  `data/records.json` (saved by `reset-for-demo.sh`) — so a draft always shows.
- **Anything else:** second terminal on `main`, already run end-to-end.

## Pre-flight checklist
- [ ] `source .venv/bin/activate`
- [ ] `bash fetch-emails.sh && bash categorize-emails.sh && bash write-replies.sh` runs clean
- [ ] `data/voice_pairs.jsonl` + `data/knowledge_index.db` present
- [ ] Claude CLI logged in, usage NOT near the limit
- [ ] Second terminal open on `main`
