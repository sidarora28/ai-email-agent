# 📧 Build Your Own Email Assistant — Attendee Guide

Welcome! Over the next hour you're going to build a real AI email assistant — one that reads your inbox, sorts it into your categories, and drafts replies that sound like *you*. You won't write any code. You'll just **talk to Claude Code in plain English**, like briefing a smart, fast teammate. You type a request, it builds the thing, you look at the result, you move on.

**One promise up front:** nothing is ever sent. Every reply your assistant writes is saved as a draft *you* review and send yourself.

---

## Before we start (5 minutes)

Two clicks, no typing:

1. **Install Claude Code** — follow the on-screen installer. When it opens, you'll have a chat box. That's where everything happens.
2. **Connect your Gmail** — open the connectors panel in Claude Code's UI and click to connect Gmail. It'll ask permission in your browser. Approve it. Done.

That's the whole setup. No downloads, no project to clone. From here on, you're just chatting.

> **How to read this guide:** each step is **one thing to ask Claude Code**, shown in a box like the ones below, plus a quick note on *why it matters*. Type the request, watch it work, then go to the next step. Feel free to use your own words — these are just examples.

---

## Step 1 — Connect and read your inbox

> Pull my most recent unread emails from Gmail and show me a short list — sender, subject, and a one-line summary of each.

**Why it matters:** This is your assistant taking its first look at your real inbox. Seeing it actually read your mail makes everything after this feel real.

---

## Step 2 — Gather your real writing

> Find emails I've sent as replies, and for each one also grab the email it was answering. Show me a handful of these reply-and-original pairs.

**Why it matters:** Your voice isn't a vibe — it's learned from how you *actually* write. Pairing each reply with the email it answered teaches the assistant not just your words, but how you respond to different situations.

---

## Step 3 — Learn your voice

> Read through those reply pairs and write a "voice profile" describing how I write — how I open, how I sign off, my tone, how long my emails are, and the phrases I lean on. Save it so we can use it later.

**Why it matters:** Read it aloud. It should sound like a friend describing how you email. This profile is what makes drafts sound like you and not a generic robot.

---

## Step 4 — Peek at how it finds the right reply

> Take two of my past replies, turn each into numbers, and tell me which two are closest in meaning. Explain in plain English what just happened.

**Why it matters:** An **embedding** is just turning a piece of text into numbers so that things that *mean* similar things sit close together. That's the trick your assistant uses to find your most relevant past reply and the right facts — no magic, just "close meanings sit close."

---

## Step 5 — Give it your facts

> Help me create a few short notes of real facts about my work — my product and pricing, any upcoming event, and my partnership terms. Keep them short and only include things that are actually true.

**Why it matters:** These notes are your assistant's source of truth. The golden rule: **no file, no fact.** If it isn't written here, the assistant isn't allowed to say it — that's what stops it from making things up.

---

## Step 6 — Make it searchable

> Build two separate searchable indexes: one for my voice profile (how I sound) and one for my fact notes (what's true). Keep them separate.

**Why it matters:** Two libraries, two jobs. One answers "how would I say this?" and the other answers "what's actually true?" Keeping them apart keeps your *style* from getting tangled up with your *facts*.

---

## Step 7 — Write your rules

> Write a "principles" file with the rules every reply must always follow: never invent a fact, never offer a discount, never make commitments on my behalf, always sound human, and never send anything — only ever save a draft. These rules override the voice profile.

**Why it matters:** Your voice profile is *style*; your principles are *policy*. **When they conflict, principles win.** Your past emails might offer a discount — but if a principle says never do that, the assistant holds back and leaves it to you.

---

## Step 8 — Discover your categories and build a classifier

> Look at my real emails and figure out the categories *I* actually deal with — don't use generic ones. Then build a classifier that tags each new email with its category, a confidence score, the sender's intent, how urgent it is, and whether it needs me personally (anything about discounts, refunds, or commitments should flag a human).

**Why it matters:** Your inbox is yours — your buckets should be too. Flagging the sensitive stuff for a human is how the assistant knows what *not* to touch on its own.

---

## Step 9 — Sort your inbox

> Run the classifier on my unread emails and show me how each one was routed — should it get a draft, come straight to me, or be skipped?

**Why it matters:** This is triage. In one pass you see your whole inbox organized by what actually needs to happen, before a single reply is written.

---

## Step 10 — Write the replies (the writer)

> For each email worth replying to, draft a response as me — in my voice, using only my real facts, and following my principles.

**Why it matters:** This is the writer agent doing its main job. Notice it only uses facts from your notes and stays inside your rules. Drafts, never sends.

---

## Step 11 — Review the replies (the reviewer)

> Have a second agent check every draft: Is it grounded in my real facts? Does it sound like me? Does it break any principle? If a draft fails, send it back to be rewritten once.

**Why it matters:** One agent writes, a different agent checks. That second pair of eyes — *grounded? sounds like you? breaks a rule?* — is the reason you can actually trust the drafts.

---

## Step 12 — Run the whole thing

> Now run the full pipeline end to end: fetch my inbox, sort it, write replies, review them, and save the results.

**Why it matters:** Everything you built clicks together into one flow. Fetch → sort → write → review → save, all in a single go.

---

## Step 13 — Approve your drafts, one at a time

> Show me my finished drafts one at a time. When I approve one, save it to my Gmail Drafts. Don't send anything.

**Why it matters:** You're the human in the loop. You approve each draft individually, and approving simply parks it in Gmail Drafts. **You hit send yourself — always.**

---

## What you walk away with

A real email assistant that triages your inbox and writes like you — and that you can actually *trust*, because it only speaks from your facts, follows your rules, and never sends a thing without you. You didn't write a line of code. You built it by directing Claude Code in plain English, the same way you'd brief a sharp teammate. That's the whole point: you described what you wanted, and it got built. Now go make it yours. 🚀
