"""classify.py — M2: route incoming emails into Sid's categories.

For each incoming email: send the classifier agent prompt + the categories M1
discovered + the email to the `claude` CLI, validate the JSON against schema.py,
apply the safety rules, and attach the category's handling map.

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
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from schema import Classification, parse_classification  # noqa: E402

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / ".claude/agents/classifier.md"
CATEGORIES = ROOT / "data/categories.yaml"        # discovered by M1
HANDLING = ROOT / "m2_classify/handling.yaml"     # editable config
INBOUND = ROOT / "data/inbound.jsonl"
OUT = ROOT / "data/classified.json"
MODEL = os.getenv("CLASSIFY_MODEL", "claude-haiku-4-5")
THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
WORKERS = int(os.getenv("CLASSIFY_WORKERS", "10"))


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
    data = yaml.safe_load(HANDLING.read_text()) or {}
    return data.get("handling", {})


def load_inbound():
    rows = []
    with INBOUND.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def call_agent(prompt):
    res = subprocess.run(
        ["claude", "-p", "--model", MODEL],
        input=prompt, capture_output=True, text=True, timeout=90,
    )
    m = re.search(r"\{.*\}", res.stdout, re.DOTALL)
    if not m:
        raise ValueError(f"No JSON from classifier: {res.stdout[:200]}")
    return json.loads(m.group(0))


def classify_one(email, base, cats, handling):
    prompt = (
        f"{base}\n\nCATEGORIES:\n{cats}\n\n"
        f"EMAIL:\nFrom: {email.get('sender','')}\n"
        f"Subject: {email.get('subject','')}\n"
        f"Body: {email.get('body', email.get('snippet',''))}\n"
    )
    raw = call_agent(prompt)
    raw.update({
        "id": email.get("id"),
        "sender": email.get("sender"),
        "subject": email.get("subject"),
        "snippet": (email.get("body") or email.get("snippet") or "")[:160],
    })
    c = parse_classification(raw)

    # --- safety rules ---
    rule = handling.get(c.category, {})
    if c.confidence < THRESHOLD or c.category == "uncertain":
        c.needs_human = True          # keep best-guess category for display
    if rule.get("escalate"):
        c.needs_human = True
    c.default_action = rule.get("default_action")
    c.tools = rule.get("tools", [])
    return c


def classify_emails(emails):
    base, cats, handling = agent_prompt(), categories_block(), handling_map()
    results = [None] * len(emails)
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = {pool.submit(classify_one, e, base, cats, handling): i
                for i, e in enumerate(emails)}
        for fut in as_completed(futs):
            i = futs[fut]
            c = results[i] = fut.result()
            done += 1
            flag = "→Sid" if c.needs_human else ("skip" if not c.reply_needed else "draft")
            print(f"  [{done}/{len(emails)}] {c.category:18} {c.urgency.value:6} "
                  f"({c.confidence}) {flag:5} {(c.subject or '')[:34]}")
    return results


def main():
    emails = load_inbound()
    print(f"Classifying {len(emails)} emails (model: {MODEL}, threshold: {THRESHOLD})\n")
    results = classify_emails(emails)
    OUT.write_text(json.dumps([c.model_dump(mode="json") for c in results], indent=2))
    n_draft = sum(1 for c in results if c.reply_needed and not c.needs_human)
    print(f"\nDone -> {OUT}")
    print(f"  {n_draft} ready to draft · {sum(c.needs_human for c in results)} to Sid · "
          f"{sum(not c.reply_needed for c in results)} no-reply")


if __name__ == "__main__":
    main()
