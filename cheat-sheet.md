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

## PART 2 — PLAY WITH IT IN CLAUDE CODE (see every piece, live)

No scripts here. I just open Claude Code and **play** — poke each piece into life,
react to what comes back, and let the audience watch. Each beat: **Ask** = roughly
what I say to Claude (my words, loose) · **Show** = what pops up on screen (the
learning) · **Say** = my line. The *Show* items are my real files — proof it's real,
not a prop. 🎲 = a "try to break it" moment; those land hardest.

---

**1. Can it even read my inbox?**

Ask: *"Get into my Gmail and pull my 10 latest unread — who's emailing me right now?"*
**Show:** my actual unread emails, live on screen.
**Say:** "That's my real inbox. We're not in a sandbox."

---

**2. How do I actually write?**

Ask: *"Go find how I've replied in the past — my sent replies plus the emails they answered. Show me a few."*
**Show:** two or three `[incoming → my reply]` pairs (`data/voice_pairs.jsonl`).
**Say:** "This is the gold — real examples of how I write, not a vibe."

---

**3. Learn me.**

Ask: *"Read those and tell me how I write — write it up as a voice profile, and tell me what kinds of email I get."*
**Show:** `data/voice_profile.md` — scroll to a section, read it aloud. Then the categories it found (`data/categories.yaml`).
**Say:** *(Opus)* "It didn't guess — it read how I actually write. That's eerie."

---

**4. Wait — how does it know what's 'similar'?**

Ask: *"Hang on, show me the trick. Turn two of my replies into numbers and tell me which two are closest in meaning."*
**Show:** the number vectors + a similarity score.
**Say:** "Meaning becomes numbers. Close numbers = close meaning. That's the whole secret."

---

**5. Give it the truth.**

Ask: *"It can't make stuff up about me — help me jot down my real facts: my pricing, the event, sponsorship."*
**Show:** `knowledge/course.md` — point at the real price ($600 / early bird $450).
**Say:** "If it's not written here, it's not allowed to say it. No file, no fact."

---

**6. Test its memory.**

Ask: *"Here's a sample email — which of my past replies and which facts would you reach for?"*
**Show:** the live retrieval — closest real reply + the matching facts.
**Say:** "It found my closest reply and the right facts, on its own."

---

**7. Lay down the law.**

Ask: *"Write the rules it can never break — no made-up facts, no discounts, no promises, and never send."*
**Show:** `principles.md` — the `[HARD RULE]` lines (discount → defer to Sid; never send).
🎲 Ask: *"Now watch — here's someone begging for a discount. What do you do?"* → it shares the price but **won't** discount; flags it to me.
**Say:** "Voice is style; principles are law. On conflict, the law wins."

---

**8. Make it sort.**

Ask: *"Build me something that reads an email and tags it — category, how urgent, and whether it needs me personally."*
**Show:** the classifier's JSON for one email + the routing rules (`m2_classify/handling.yaml`).
**Say:** *(Haiku)* "My buckets, not generic ones. And the spicy stuff gets flagged to me."

---

**9. Triage the whole inbox.**

Ask: *"Run that across everything unread — what would you draft, what comes to me, what do we ignore?"*
**Show:** the routing list (`data/classified.json`) — draft / → Sid / skip, per email.
**Say:** "Whole inbox sorted in one pass — before a single reply is written."

---

**10. The fun part — write as me.**

Ask: *"Okay, write a reply to this one as me."*
**Show:** the draft typing itself out, token by token.
**Say:** *(Opus)* "Watch it write — that's my voice, grounded in my facts."

---

**11. But can I trust it?**

Ask: *"Add a second AI to grade that draft — is it grounded? does it sound like me? does it break a rule?"*
**Show:** the verdict — `grounded ✓ · voice ✓ · approve` — and `.claude/agents/reviewer.md`.
🎲 Ask: *"Now sneak a wrong price into the draft and see if the reviewer catches it."* → it flags **not grounded** and sends it back.
**Say:** "One writes, one checks. That's why I can trust it."

---

**12. Run the whole thing for real.**

Ask: *"Do it all now — fetch, sort, write, review, save everything."*
**Show:** the full run scrolling through each email, then `data/records.json` with the finished drafts.
**Say:** "Top to bottom, hands off — until I step in."

---

**13. I have the final say.**

Ask: *"Show me the drafts one by one — I'll approve the good ones into Gmail."*
**Show:** the numbered list → approve one → flip to **Gmail › Drafts**, there it sits, unsent.
**Say:** "It drafts. I send. Always."

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
