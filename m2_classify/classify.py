"""classify.py — M2: route incoming emails into Sid's categories.

Sends the classifier prompt + the categories M1 discovered + ALL inbound emails
to the `claude` CLI in ONE batched call (returns a JSON array), validates each
against schema.py, applies the safety rules, and attaches the handling map.

One call (not one-per-email) keeps it fast and avoids spawning many CLIs at once.

    python m2_classify/classify.py

Input:  data/inbound.jsonl   (one {id, sender, subject, body} per line)
Output: data/classified.json

Safety rules:
- confidence < threshold OR category == "uncertain"  -> needs_human = true
- category's handling.escalate is true               -> needs_human = true
- reply_needed == false (automated mail)             -> no draft downstream
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from schema import parse_classification  # noqa: E402

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / ".claude/agents/classifier.md"
CATEGORIES = ROOT / "data/categories.yaml"
HANDLING = ROOT / "m2_classify/handling.yaml"
INBOUND = ROOT / "data/inbound.jsonl"
OUT = ROOT / "data/classified.json"
MODEL = os.getenv("CLASSIFY_MODEL", "claude-haiku-4-5-20251001")
THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))


def agent_prompt():
    text = AGENT.read_text()
    return re.sub(r"^---.*?---\s*", "", text, count=1, flags=re.DOTALL).strip()


def categories_block():
    data = yaml.safe_load(CATEGORIES.read_text()) or {}
    return "\n".join(
        f"- {c['name']}: {c.get('description','').strip()}"
        for c in data.get("categories", [])
    )


def handling_map():
    return (yaml.safe_load(HANDLING.read_text()) or {}).get("handling", {})


def load_inbound():
    rows = []
    with INBOUND.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_prompt(emails, base, cats):
    blocks = []
    for i, e in enumerate(emails):
        body = (e.get("body") or e.get("snippet") or "")[:1500]
        blocks.append(
            f"[{i}] From: {e.get('sender','')}\n"
            f"Subject: {e.get('subject','')}\n"
            f"Body: {body}"
        )
    return (
        f"{base}\n\nCATEGORIES:\n{cats}\n\n"
        f"Classify EACH email below. Return ONLY a JSON array with one object per "
        f"email, IN THE SAME ORDER, each shaped exactly:\n"
        f'{{"category": "...", "confidence": 0.0, "intent": "...", '
        f'"urgency": "high|medium|low", "needs_human": false, "reply_needed": true}}\n\n'
        f"EMAILS:\n" + "\n\n".join(blocks)
    )


def call_agent(prompt):
    res = subprocess.run(
        ["claude", "-p", "--model", MODEL],
        input=prompt, capture_output=True, text=True, timeout=180,
    )
    if res.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {res.stderr[:300]}")
    m = re.search(r"\[.*\]", res.stdout, re.DOTALL)
    if not m:
        raise ValueError(f"No JSON array from classifier: {res.stdout[:300]}")
    return json.loads(m.group(0))


def main():
    emails = load_inbound()
    handling = handling_map()
    print(f"Classifying {len(emails)} emails in one batched call (model: {MODEL}) ...\n")

    raw_list = call_agent(build_prompt(emails, agent_prompt(), categories_block()))
    if len(raw_list) != len(emails):
        print(f"  warning: got {len(raw_list)} results for {len(emails)} emails")

    results = []
    for email, raw in zip(emails, raw_list):
        raw.update({
            "id": email.get("id"),
            "sender": email.get("sender"),
            "subject": email.get("subject"),
            "snippet": (email.get("body") or email.get("snippet") or "")[:160],
        })
        c = parse_classification(raw)
        rule = handling.get(c.category, {})
        if c.confidence < THRESHOLD or c.category == "uncertain":
            c.needs_human = True
        if rule.get("escalate"):
            c.needs_human = True
        c.default_action = rule.get("default_action")
        c.tools = rule.get("tools", [])
        results.append(c)
        flag = "→Sid" if c.needs_human else ("skip" if not c.reply_needed else "draft")
        print(f"  {c.category:18} {c.urgency.value:6} ({c.confidence}) {flag:5} "
              f"{(c.subject or '')[:34]}")

    OUT.write_text(json.dumps([c.model_dump(mode="json") for c in results], indent=2))
    n_draft = sum(1 for c in results if c.reply_needed and not c.needs_human)
    print(f"\nDone -> {OUT}")
    print(f"  {n_draft} ready to draft · {sum(c.needs_human for c in results)} to Sid · "
          f"{sum(not c.reply_needed for c in results)} no-reply")


if __name__ == "__main__":
    main()
