# Email Classifier Toolkit

A tiny, self-contained starter kit for classifying inbound email with a
**Claude Code agent**. Drop your Claude Code agent here, run, classify.

It reads a category taxonomy (YAML), sends each email + your agent prompt to
the `claude` CLI in parallel, validates the result against a Pydantic schema,
and writes `classified.json`. Swap the taxonomy to match your persona (founder,
creator, support team, sales rep, exec) — or write your own.

Everything is synthetic and runs offline against a sample inbox, so a stranger
can clone this and see it work in under five minutes.

## Prerequisites

- **Python 3.11+**
- **Claude Code installed** — the `claude` CLI must be on your PATH and
  authenticated. (Run `claude --version` to confirm.)

## Setup

Copy-paste, top to bottom:

```bash
# 1. From the repo root, create and activate a virtual env
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install the (tiny) dependency set
pip install -r requirements.txt

# 3. Run it — classifies the sample inbox with the founder taxonomy
python classify.py
```

You'll see each email classified as it completes, then a `classified.json`
written to the repo root. That's it.

## How it works

```
examples/sample_inbound.json   ─┐
taxonomies/founder.yaml         ├─►  claude CLI (per email, in parallel)  ─►  classified.json
.claude/agents/classifier.md   ─┘         (validated against schema.py)
```

- `classify.py` runs one `claude -p ... --model claude-haiku-4-5-20251001` call
  per email, concurrently via a `ThreadPoolExecutor` (default 10 workers —
  sequential would be painfully slow).
- Each call returns a single JSON object that's validated by `schema.py`
  (`category`, `urgency`, `suggested_action`, `confidence`).

## Swap taxonomies

The taxonomy is just a YAML file with a `categories:` list. Five are included
in `taxonomies/`: `founder`, `creator`, `support-team`, `sales`, `exec`.

Pick one with a CLI arg:

```bash
python classify.py taxonomies/sales.yaml
```

...or with an env var:

```bash
CLASSIFY_TAXONOMY=taxonomies/exec.yaml python classify.py
```

To make your own, copy any file in `taxonomies/`, keep the
`categories:` → `name` / `description` shape, and point `classify.py` at it.

### Other knobs (all optional env vars)

| Variable            | Default                          | What it does                       |
| ------------------- | -------------------------------- | ---------------------------------- |
| `CLASSIFY_TAXONOMY` | `taxonomies/founder.yaml`        | Which category set to use          |
| `CLASSIFY_INBOUND`  | `examples/sample_inbound.json`   | Which inbox to classify            |
| `CLASSIFY_MODEL`    | `claude-haiku-4-5-20251001`      | Which model the CLI calls          |
| `CLASSIFY_WORKERS`  | `10`                             | Parallel agent calls               |

Put them in a `.env` file (auto-loaded) or pass them inline.

## Bring your own agent

The classification logic lives entirely in `.claude/agents/classifier.md`.
Edit that prompt — or drop in your own Claude Code agent — and rerun. The
Python is just plumbing: read inbox, fan out to the agent, validate, save.

## A note on the numbers

> Magic numbers used (0.7 confidence). Cohort week 2 teaches you to find yours.

See `extension-notes.md` for the eval / threshold-tuning / multi-label /
active-learning path, and `prompts/confidence-patterns.md` for how to reason
about confidence scores.
