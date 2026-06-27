# Extension Notes

Where to take this v0.1 starter next. These are the threads the cohort pulls on
in weeks 3-4 — here as signposts so you can explore on your own first.

## Multi-agent pattern selection
- This template uses the simplest useful shape: a **two-agent pipeline**
  (drafter → reviewer). It's a linear handoff, not a debate or a swarm.
- Pick the pattern to fit the task: **pipeline** for "produce then critique",
  **router** for "classify then dispatch to specialists", **reflection loop**
  for "draft → critique → revise until the reviewer approves (capped retries)".
- Resist adding agents. Each hop adds latency, cost, and failure modes. Add a
  reviewer only when an independent check measurably improves output quality.

## Reviewer prompt engineering
- The reviewer returns **structured JSON** (`verdict` / `comment` /
  `suggested_edit`) so the program can branch on it — prose verdicts are hard
  to act on. We parse defensively (`re.search(r"\{.*\}")`) and fail open.
- Give the reviewer an explicit rubric (voice, answer, accuracy, length). Vague
  reviewers rubber-stamp everything.
- Next step: turn the reviewer into a real **gate** — on `revise`, feed
  `suggested_edit` back to the drafter and loop (with a max-iterations cap).

## Auth / persistence / monitoring (cohort weeks 3-4)
- **Auth**: this dashboard is wide open. Add SSO / login before anyone but you
  can see drafts; never expose unsent replies publicly.
- **Persistence**: drafts live in a flat `drafts.json`. Move to a database so
  edits, send-state, and audit history survive restarts and concurrency.
- **Monitoring**: log every `claude` call (latency, tokens, verdict
  distribution) and alert on reviewer error rates and timeouts.

## Deploy hardening
- Wire the Send/Edit/Skip buttons to a real outbox with human-in-the-loop
  confirmation and idempotency (don't double-send on a rerun).
- Add retries + backoff around the `claude` subprocess, and a per-email
  timeout budget so one slow draft can't stall the pool.
- Containerize, pin the model version, and put secrets in a real secret store
  rather than `.env`.
