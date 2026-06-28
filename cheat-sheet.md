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

I don't run scripts here. I **direct Claude Code** in plain English. Type the prompt, narrate the point.

**1. Connect Gmail**
> Connect to my Gmail and pull my 10 most recent unread emails.

> "First, prove it can read my inbox."

**2. Fetch sent pairs**
> Now fetch my sent replies along with the original email each one was answering, and save them as pairs.

> "This is the raw material for my voice."

**3. Learn voice**
> Read those pairs and write me a voice profile — my openings, sign-offs, tone, typical length, and recurring phrases. Use a strong model for this.

> *(Opus)* Read a line aloud — "yep, that's how I write."

**4. Embeddings demo**
> Turn two of my replies into number vectors and show me which two are closest in meaning.

> "This is the magic, demystified — similar meaning, close numbers."

**5. Add knowledge**
> Create short files of my real facts — one for the course, one for the event, one for sponsorship and pricing.

> "It can only state facts that live here. No file, no fact."

**6. Build indexes**
> Build two separate searchable indexes — one for my voice, one for my knowledge.

> "One teaches how I sound, one supplies what's true."

**7. Principles**
> Write an always-on principles file that overrides the voice profile: never invent a fact, never offer a discount, never commit on my behalf, always sound human, and never send — only draft.

> "Voice is style, principles are policy. On conflict, principles win."

**8. Categories + classifier**
> Discover my own categories from my real email, then build a classifier that tags each email with category, confidence, intent, urgency, and needs_human. Use a fast model.

> *(Haiku)* "My inbox, my buckets. Discounts, refunds, commitments — flag a human."

**9. Sort inbox**
> Run the classifier on my unread mail and show me the routing — draft, send to me, or skip.

> "Now it knows what to do with each one."

**10. Writer**
> Write a drafter that replies as me — my voice, only my facts, my principles — and stream it as it writes. Use a strong model.

> *(Opus)* "Watch it write in my voice."

**11. Reviewer**
> Add a second agent that checks each draft: is it grounded against the full knowledge, does it sound like me, does it break any principle? Send it back for one rewrite if needed. Use a fast model.

> *(Haiku)* "One writes, one checks. That's the trust."

**12. Run end to end**
> Run the whole pipeline now — fetch, sort, write, review, and save the records.

> "Top to bottom, no hands."

**13. Approve one at a time**
> List the finished drafts with numbers, and let me approve them one by one — approving creates a Gmail draft, never sends.

> "Human in the loop. I send every email myself."

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
