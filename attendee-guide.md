# 📧 Build Your Own Email Assistant — Attendee Guide

Welcome! Over the next hour you're going to build a real AI email assistant — one that reads your inbox, sorts it into your categories, and drafts replies that sound like *you*. You won't write any code. You'll just **talk to Claude Code in plain English**, like briefing a smart, fast teammate. You type a request, it builds the thing, you look at the result, you move on.

**One promise up front:** nothing is ever sent. Every reply your assistant writes is saved as a draft *you* review and send yourself.

---

## Before we start (5 minutes)

Two clicks, no typing:

1. **Install Claude Code** — follow the on-screen installer. When it opens, you'll have a chat box. That's where everything happens.
2. **Connect your Gmail** — open the connectors panel in Claude Code's UI and click to connect Gmail. It'll ask permission in your browser. Approve it. Done.

That's the whole setup. No downloads, no project to clone. From here on, you're just chatting.

> **How to read this guide:** each step is **one thing to ask Claude Code**, shown in a code block, plus a quick note on *why it matters*. Copy the request, paste it in, watch it work, then go to the next step. These are the same prompts used in the live build — feel free to tweak them in your own words.

---

## Step 1 — Connect and read your inbox

```text
Connect to my Gmail and pull my 10 most recent unread emails. For each one,
show me the sender, the subject, and a one-line summary, so I can see you're
really reading my inbox.
```

**Why it matters:** This is your assistant taking its first look at your real inbox. Seeing it actually read your mail makes everything after this feel real.

---

## Step 2 — Gather your real writing

```text
Go through my Gmail and find emails I sent as replies. For each reply, also
grab the original email I was answering, and save them together as "reply +
original" pairs. Get a few dozen so there's enough to learn from, then show me
a handful of the pairs.
```

**Why it matters:** Your voice isn't a vibe — it's learned from how you *actually* write. Pairing each reply with the email it answered teaches the assistant not just your words, but how you respond to different situations.

---

## Step 3 — Learn your voice

```text
Read through those reply pairs and write me a "voice profile" — a short
document describing how I write: how I open and sign off, my tone, how long my
emails usually are, the phrases I lean on, and things I'd never say. Use a
strong model (Opus) for this, and save the profile so we can reuse it later.
```

**Why it matters:** Read it aloud. It should sound like a friend describing how you email. This profile is what makes drafts sound like you and not a generic robot.

---

## Step 4 — Peek at how it finds the right reply

```text
Take two of my past replies, turn each one into an embedding (a list of numbers
that captures its meaning), and tell me which two are closest. Then explain in
plain English what just happened and why "closer numbers" means "closer meaning."
```

**Why it matters:** An **embedding** is just turning a piece of text into numbers so that things that *mean* similar things sit close together. That's the trick your assistant uses to find your most relevant past reply and the right facts — no magic, just "close meanings sit close."

---

## Step 5 — Give it your facts

```text
Help me write a few short notes of real facts about my work — one for my
product and its pricing, one for any upcoming event, and one for my
partnership/sponsorship terms. Keep them short and only include things that are
actually true. These notes are the only facts you're allowed to use in replies.
```

**Why it matters:** These notes are your assistant's source of truth. The golden rule: **no file, no fact.** If it isn't written here, the assistant isn't allowed to say it — that's what stops it from making things up.

---

## Step 6 — Make it searchable

```text
Build two separate searchable indexes: one over my voice profile and example
replies (how I sound), and one over my fact notes (what's true). Keep them
separate so my style never gets mixed up with my facts.
```

**Why it matters:** Two libraries, two jobs. One answers "how would I say this?" and the other answers "what's actually true?" Keeping them apart keeps your *style* from getting tangled up with your *facts*.

---

## Step 7 — Write your rules

```text
Write me a "principles" file — the always-on rules every reply must follow:
never state a fact that isn't in my notes, never offer or negotiate a discount,
never make commitments or promises on my behalf, always sound human (not
robotic), and never send anything — only ever save a draft. Make it clear these
rules override my voice profile: if my past style conflicts with a rule, the
rule wins.
```

**Why it matters:** Your voice profile is *style*; your principles are *policy*. **When they conflict, principles win.** Your past emails might offer a discount — but if a principle says never do that, the assistant holds back and leaves it to you.

---

## Step 8 — Discover your categories and build a classifier

```text
Look at my real emails and work out the categories I actually deal with — my
own buckets, not generic ones. Then build a classifier that reads a new email
and tags it with: its category, a confidence score, the sender's intent, how
urgent it is, and whether it needs me personally. Anything about discounts,
refunds, or commitments should be flagged for a human. Use a fast, cheap model
(Haiku).
```

**Why it matters:** Your inbox is yours — your buckets should be too. Flagging the sensitive stuff for a human is how the assistant knows what *not* to touch on its own.

---

## Step 9 — Sort your inbox

```text
Run the classifier on my unread emails and show me how each one was routed —
which should get an auto-draft, which should come straight to me, and which to
skip — with the category and a short reason for each.
```

**Why it matters:** This is triage. In one pass you see your whole inbox organized by what actually needs to happen, before a single reply is written.

---

## Step 10 — Write the replies (the writer)

```text
Build the "writer": for each email worth a reply, draft a response as me — in
my voice, using only the facts in my notes, and following my principles. Stream
the reply as it writes so I can watch it come together. Use a strong model (Opus).
```

**Why it matters:** This is the writer agent doing its main job. Notice it only uses facts from your notes and stays inside your rules. Drafts, never sends.

---

## Step 11 — Review the replies (the reviewer)

```text
Add a second agent, the "reviewer," that checks every draft before I see it: is
every fact grounded in my full set of notes, does it sound like me, and does it
break any principle? If a draft fails any check, send it back to the writer to
be rewritten once. Use a fast model (Haiku).
```

**Why it matters:** One agent writes, a different agent checks. That second pair of eyes — *grounded? sounds like you? breaks a rule?* — is the reason you can actually trust the drafts.

---

## Step 12 — Run the whole thing

```text
Now run the whole thing end to end: fetch my unread inbox, sort it, write
replies for the ones that need them, review each draft, and save all the
results so I can look at them.
```

**Why it matters:** Everything you built clicks together into one flow. Fetch → sort → write → review → save, all in a single go.

---

## Step 13 — Approve your drafts, one at a time

```text
Show me my finished drafts one at a time, numbered. Let me approve them one by
one — when I approve one, save it to my Gmail Drafts. Never send anything; I'll
hit send myself.
```

**Why it matters:** You're the human in the loop. You approve each draft individually, and approving simply parks it in Gmail Drafts. **You hit send yourself — always.**

---

## What you walk away with

A real email assistant that triages your inbox and writes like you — and that you can actually *trust*, because it only speaks from your facts, follows your rules, and never sends a thing without you. You didn't write a line of code. You built it by directing Claude Code in plain English, the same way you'd brief a sharp teammate. That's the whole point: you described what you wanted, and it got built. Now go make it yours. 🚀
