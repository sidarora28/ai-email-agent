"""api.py — non-interactive bridge for the dashboard UI.

Reuses the engine + approve helpers (no streaming, JSON in/out) so the Next.js
app can drive the pipeline without touching the live-demo CLI (engine.py).

    python m3_engine/api.py inbox                      # classified + draft status, as JSON
    python m3_engine/api.py draft --ids <id1,id2,...>  # draft+review just those, merge records
    python m3_engine/api.py approve --id <id> [--body "edited text"]   # -> Gmail draft

Everything prints a single JSON object/array to stdout. Errors -> {"error": "..."}.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))

# Heavy pipeline imports (engine -> chromadb/torch) are done lazily inside draft()
# so `inbox` and `approve` stay fast and don't need the embedding stack.

CLASSIFIED = ROOT / "data/classified.json"
RECORDS = ROOT / "data/records.json"


def load_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def route_of(e):
    """How this email is routed, for the UI."""
    if not e.get("reply_needed"):
        return "skip"
    if e.get("needs_human"):
        return "needs_human"
    return "draft"


def inbox():
    """Classified emails + their current draft status, for the dashboard."""
    classified = load_json(CLASSIFIED, [])
    records = {r.get("id"): r for r in load_json(RECORDS, [])}
    out = []
    for e in classified:
        rec = records.get(e.get("id"))
        out.append({
            "id": e.get("id"),
            "sender": e.get("sender"),
            "subject": e.get("subject"),
            "snippet": e.get("snippet"),
            "category": e.get("category"),
            "intent": e.get("intent"),
            "urgency": e.get("urgency"),
            "confidence": e.get("confidence"),
            "needs_human": e.get("needs_human"),
            "reply_needed": e.get("reply_needed"),
            "route": route_of(e),
            "status": rec.get("status") if rec else None,
            "draft": rec.get("draft") if rec else None,
            "review": rec.get("review") if rec else None,
        })
    return out


def draft_one(email, principles, profile, knowledge_full):
    """Draft + review a single email (no streaming). Mirrors engine.main's body."""
    import engine
    from retrieve import retrieve_voice, retrieve_knowledge
    query = f"{email.get('subject','')} {email.get('body') or email.get('snippet','')}"
    try:
        voice_ex = retrieve_voice(query, 3)
        knowledge = retrieve_knowledge(query, 4)
    except Exception as e:
        voice_ex, knowledge = [], []
        sys.stderr.write(f"retrieve failed: {e}\n")
    connectors = engine.run_connectors(email)

    draft = engine.claude(
        engine.draft_prompt(email, voice_ex, knowledge, connectors, principles, profile),
        engine.DRAFT_MODEL)
    if draft.startswith("NO_DRAFT"):
        return {**email, "status": "insufficient_info", "draft": "", "review": {"comment": draft}}

    closest = voice_ex[0]["text"] if voice_ex else ""
    rev = engine.review(engine.review_prompt(email, draft, knowledge_full, closest, connectors, principles))
    if rev.get("verdict") == "revise":
        draft = engine.claude(
            engine.draft_prompt(email, voice_ex, knowledge, connectors, principles,
                                profile, feedback=rev.get("comment", "")), engine.DRAFT_MODEL)
        rev = engine.review(engine.review_prompt(email, draft, knowledge_full, closest, connectors, principles))
    return {**email, "status": "drafted", "draft": draft, "review": rev}


def draft(ids):
    import engine
    classified = {e.get("id"): e for e in load_json(CLASSIFIED, [])}
    principles = engine.body(engine.PRINCIPLES)
    profile = engine.VOICE_PROFILE.read_text() if engine.VOICE_PROFILE.exists() else ""
    knowledge_full = engine.full_knowledge()

    records = {r.get("id"): r for r in load_json(RECORDS, [])}
    done = []
    for eid in ids:
        email = classified.get(eid)
        if not email:
            continue
        try:
            rec = draft_one(email, principles, profile, knowledge_full)
        except Exception as e:
            rec = {**email, "status": "error", "draft": "", "review": {"comment": str(e)[:160]}}
        records[eid] = rec
        done.append(rec)

    # preserve classified order in the saved file
    order = [e.get("id") for e in load_json(CLASSIFIED, [])]
    merged = [records[i] for i in order if i in records]
    RECORDS.write_text(json.dumps(merged, indent=2))
    return done


def approve(eid, body=None):
    from approve import service, make_draft, email_addr
    records = load_json(RECORDS, [])
    rec = next((r for r in records if r.get("id") == eid), None)
    if not rec:
        return {"error": f"no record {eid}"}
    text = body if body is not None else rec.get("draft", "")
    if not text:
        return {"error": "empty draft"}
    svc = service()
    make_draft(svc, email_addr(rec.get("sender", "")), rec.get("subject", ""), text)
    rec["draft"] = text
    rec["status"] = "approved"
    RECORDS.write_text(json.dumps(records, indent=2))
    return {"ok": True, "id": eid}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("inbox")
    d = sub.add_parser("draft")
    d.add_argument("--ids", required=True)
    a = sub.add_parser("approve")
    a.add_argument("--id", required=True)
    a.add_argument("--body", default=None)
    args = ap.parse_args()

    try:
        if args.cmd == "inbox":
            result = inbox()
        elif args.cmd == "draft":
            result = draft([i for i in args.ids.split(",") if i])
        elif args.cmd == "approve":
            result = approve(args.id, args.body)
    except Exception as e:
        print(json.dumps({"error": str(e)[:200]}))
        sys.exit(1)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
