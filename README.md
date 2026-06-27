# 📬 Email Assistant

An AI assistant that triages your inbox and drafts replies **in your voice** —
grounded in your real facts so it never hallucinates, and governed by your
principles. Built for the BWCC masterclass.

> **Status: rebuild in progress.** The engine (M1–M3) and a Claude-designed
> dashboard (M4) are being built milestone by milestone against the requirements.

## Architecture

```
M1  Learn my voice + establish sources of truth
      • voice pairs (sent reply + the email it answered)
      • voice profile (Opus 4.8, by situation) + Voice index
      • Knowledge index (course / event / sponsorship)
      • principles.md (always-on guardrails)
      • live connectors: Calendar · Beehiiv · Stripe
M2  Classify an incoming email (category + confidence + intent + urgency + flags)
M3  Engine: fetch → classify → draft → review → persist records.json
M4  Claude-designed Next.js dashboard (reads records, triggers the engine)
```

## Layout

```
principles.md          always-on rules for drafting + review
knowledge/             course.md · event.md · sponsorship.md  (sources of truth)
m1_voice/              fetch pairs · learn voice · build indexes
data/                  gitignored — voice pairs, indexes, records (local only)
```

Nothing is ever sent automatically — every reply is a draft for Sid to review.
