# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes, merged with
project-specific instructions for the Email Assistant.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken. Match existing style.
- Remove imports/variables/functions that YOUR changes made unused; leave pre-existing dead code (mention it, don't delete).

The test: every changed line should trace directly to the request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals ("Fix the bug" → "Write a test that reproduces it, then make it pass"). For multi-step work, state a brief plan with a verify step each, then loop until it passes.

---

## Project: Email Assistant

An AI email assistant for Sid (JustAnotherPM; BWCC cohort). It learns Sid's voice,
classifies incoming email, and drafts grounded replies in his voice.
**Nothing is ever sent automatically — every reply is a draft Sid reviews.**

### Architecture (milestones)
- **M1 — Voice + sources of truth** (`m1_voice/`, `knowledge/`, `principles.md`): fetch [reply + the email it answered] pairs → Opus 4.8 writes `voice_profile.md` + `categories.yaml` → voice index (reviewer) + knowledge index (drafter).
- **M2 — Classify** *(next)*: incoming email → category + confidence + intent + urgency + flags.
- **M3 — Engine** *(next)*: fetch → classify → draft → review → `data/records.json`.
- **M4 — Dashboard** *(next)*: Claude-designed Next.js app; reads records, triggers the engine.

### Project rules (non-negotiable)
- **Grounding:** the drafter may only state facts from the knowledge index or a live
  connector (Beehiiv/Stripe/Calendar). No invented facts. The reviewer verifies against
  the **full** `knowledge/*.md` + connector results — not just retrieved chunks.
- **Voice vs policy:** `voice_profile.md` is *style*; `principles.md` is *policy*. **On
  conflict, principles win** (the profile shows Sid offering discounts; the assistant
  never does — it defers to Sid).
- **Models:** voice profile = `claude-opus-4-8`; classifier = `claude-haiku-4-5`. Agents
  run via the `claude` CLI (no API key).
- **Data:** all of `data/` is gitignored — PII / regenerable. Secrets in `data/auth/` + `.env`. Never commit either.
