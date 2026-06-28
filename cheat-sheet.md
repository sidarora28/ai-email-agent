# 🎬 Build with Claude Code — Stage Script

*Email Assistant: reads my inbox → sorts into MY categories → drafts in MY voice (grounded in MY real facts) → a second agent reviews each draft → approved ones saved to Gmail Drafts. **Nothing is ever sent. Every reply is a draft I review.***

---

## PART 1 — COLD OPEN (the finished product, live in the TERMINAL)

Run the built thing on my real inbox first. These are terminal commands.

**Pull the inbox**
```
bash fetch-emails.sh
```
> "It pulls my unread inbox."

**Sort it**
```
bash categorize-emails.sh
```
> "It sorts them into MY categories, not generic ones."

**Draft + review**
```
bash write-replies.sh
```
> "Watch it draft in my voice — and a second agent review each one."

**List the drafts**
```
bash approve-replies.sh
```
> "Here are my drafts, numbered."

**Approve ONE**
```
bash approve-replies.sh 2
```
> "I approve them one at a time — this one becomes a Gmail draft, never sent."

### 🎤 Audience hook
1. "Email me right now." → wait ~30s.
2. Re-run, in order:
```
bash fetch-emails.sh
```
```
bash categorize-emails.sh
```
```
bash write-replies.sh
```
> "Drafted live, in my voice, from an email that didn't exist 30 seconds ago."

### ⚠️ If it wobbles
- Second terminal stays on the working `main` branch — switch to it.
- `write-replies` auto-falls-back to the last good drafts if usage limits hit. Keep going.

---

## PART 2 — THE LIVE BUILD (all in CLAUDE CODE, no scripts)

I don't run scripts here — I **direct Claude Code** to build each piece. Each step:
**Ask** = the prompt I type · **Show** = the concrete thing I put on screen (the
learning) · **Say** = my line. The *Show* items are my real system files — that's
the proof it's actually built, not a demo prop.

---

**1. Connect Gmail**

Ask:
```text
Connect to my Gmail and pull my 10 most recent unread emails. For each one,
show me the sender, the subject, and a one-line summary.
```
**Show:** the real unread emails listed on screen.
**Say:** "First, prove it can read my actual inbox."

---

**2. Fetch sent pairs**

Ask:
```text
Now find emails I sent as replies, and for each one also grab the original
email I was answering. Save them as "reply + original" pairs and show me a few.
```
**Show:** two or three `[incoming → my reply]` pairs (`data/voice_pairs.jsonl`).
**Say:** "This is the raw material for my voice — real examples, not a vibe."

---

**3. Learn voice**

Ask:
```text
Read those reply pairs and write a voice profile — one section per situation I
write in (tone, length, openings/sign-offs, a couple of verbatim phrases I use).
Then list the categories you discovered. Use a strong model.
```
**Show:** `data/voice_profile.md` — scroll to one section, read it aloud. Then the discovered category list (`data/categories.yaml`).
**Say:** *(Opus)* "It didn't guess — it read how I actually write. Yep, that's me."

---

**4. Embeddings demo**

Ask:
```text
Take two of my past replies, turn each into an embedding (numbers that capture
meaning), and tell me which two are closest. Explain why closer numbers means
closer meaning.
```
**Show:** the actual number vectors + a similarity score on screen.
**Say:** "Similar meaning, close numbers. That's the whole trick — no magic."

---

**5. Add knowledge**

Ask:
```text
Help me write short notes of my real facts — one for the course and its
pricing, one for the event, one for sponsorship. Only things that are true.
These are the only facts you're allowed to use.
```
**Show:** `knowledge/course.md` — point at the real price line ($600 / early bird $450).
**Say:** "It can only state facts that live here. No file, no fact."

---

**6. Build indexes**

Ask:
```text
Build two separate searchable indexes — one over my voice, one over my
knowledge. Then take a sample email and show me the closest past reply and the
facts you'd pull for it.
```
**Show:** a live retrieval — paste a sample email, show the closest real reply + the matching facts it returns.
**Say:** "Ask it anything — it finds my closest reply and the relevant facts."

---

**7. Principles**

Ask:
```text
Write a principles file — the always-on rules every reply must follow: never
invent a fact, never offer a discount, never commit on my behalf, sound human,
never send (only draft). Make clear these override the voice profile.
```
**Show:** `principles.md` — point at the `[HARD RULE]` lines (discount → defer to Sid; never send).
**Say:** "Voice is style; principles are policy. On conflict, principles win."

---

**8. Categories + classifier**

Ask:
```text
Discover my own categories from my real email, then build a classifier that
tags each email with category, confidence, intent, urgency, and needs_human.
Use a fast model.
```
**Show:** the classifier's JSON for one email + the routing rules (`m2_classify/handling.yaml`).
**Say:** *(Haiku)* "My inbox, my buckets. Discounts, refunds, commitments → flag me."

---

**9. Sort inbox**

Ask:
```text
Run the classifier on my unread mail and show me the routing — which to draft,
which come to me, which to skip — with the category and reason for each.
```
**Show:** the routing list (`data/classified.json`) — draft / → Sid / skip, per email.
**Say:** "One pass, whole inbox triaged — before a single reply is written."

---

**10. Writer**

Ask:
```text
Build the writer: for each reply-worthy email, draft a response as me — my
voice, only my facts, my principles — and stream it as it writes. Use a strong
model.
```
**Show:** a draft writing itself token-by-token on screen.
**Say:** *(Opus)* "Watch it write in my voice, grounded in my facts."

---

**11. Reviewer**

Ask:
```text
Add a second agent that checks each draft: grounded against my full knowledge?
sounds like me? breaks a principle? Send it back for one rewrite if it fails.
Use a fast model.
```
**Show:** the reviewer's verdict on a draft — `grounded ✓ · voice ✓ · approve` — and `.claude/agents/reviewer.md` (the exact instruction it runs).
**Say:** *(Haiku)* "One writes, one checks. That's why I can trust it."

---

**12. Run end to end**

Ask:
```text
Now run the whole pipeline — fetch, sort, write, review — and save the results.
```
**Show:** the full run scrolling through each email, then `data/records.json` with the finished drafts.
**Say:** "Top to bottom, no hands."

---

**13. Approve one at a time**

Ask:
```text
List my finished drafts with numbers, and let me approve them one by one —
approving creates a Gmail draft, never sends.
```
**Show:** the numbered list → approve one → switch to **Gmail › Drafts** and show it sitting there, unsent.
**Say:** "Human in the loop. I send every email myself."

---

### Models (mention lightly)
- Voice profile + writer → **claude-opus-4-8**
- Classifier + reviewer → **claude-haiku-4-5-20251001**

> **Sid only — do NOT say:** `claude-sonnet-4-6` is NOT available and hangs — never use it. Parallel `claude` calls hang the laptop — keep everything sequential.

---

## ✅ PRE-FLIGHT
- [ ] Gmail connected in Claude Code
- [ ] All four cold-open scripts ran clean once beforehand
- [ ] Voice pairs + knowledge index present
- [ ] Claude CLI logged in and NOT near usage limit
- [ ] Second terminal open on `main`
