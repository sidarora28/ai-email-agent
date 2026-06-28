# 🖥️ Email Assistant — Dashboard

A small Next.js UI to run the pipeline **manually**: see your classified inbox,
**tick which emails to draft replies for**, watch the writer + reviewer run, edit a
draft, and **approve it into Gmail Drafts** (never sends). It reuses the Python
engine via a thin bridge (`m3_engine/api.py`) — no logic is duplicated.

## Run it

```bash
cd ~/Documents/Projects/email-agents
git pull origin main

cd dashboard
npm install        # first time only
npm run dev        # http://localhost:3000
```

That's it — open http://localhost:3000.

## What it expects

The UI reads what the pipeline already produces, so run the first two steps once
so there's an inbox to show:

```bash
# from the repo root, with your venv active
bash fetch-emails.sh
bash categorize-emails.sh
```

- **Drafting** selected emails runs the `claude` CLI sequentially (same as
  `write-replies.sh`) and writes `data/records.json`.
- **Approve** creates a Gmail draft via `gmail.compose`. The first approve opens a
  browser once to grant the compose scope (separate token; your read token is
  untouched). **It never sends.**

## Notes

- The bridge auto-uses the repo's `.venv/bin/python` if present, else `python3`.
  Make sure the engine's dependencies are installed in that environment.
- Live Stripe/Beehiiv lookups (e.g. "did my payment go through?") fire during
  drafting if `STRIPE_API_KEY` / `BEEHIIV_API_KEY` are set in `.env`; otherwise the
  draft safely asks for the info instead of guessing.
- `node_modules/` and `.next/` are gitignored.
