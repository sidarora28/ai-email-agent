# 📧 Build Your Own Email Assistant — Attendee Guide

Welcome! Over the next hour you're going to build a real AI email assistant — one that reads your inbox, sorts it into your categories, and drafts replies that sound like *you*. You won't write any code. You'll just **talk to Claude Code in plain English**, like briefing a smart, fast teammate. You type a request, it builds the thing, you look at the result, you move on.

**One promise up front:** nothing is ever sent. Every reply your assistant writes is saved as a draft *you* review and send yourself.

---

## Before we start (5 minutes)

Two clicks, no typing:

1. **Install Claude Code** — follow the on-screen installer. When it opens, you'll have a chat box. That's where everything happens.
2. **Connect your Gmail** — open the connectors panel in Claude Code's UI and click to connect Gmail. It'll ask permission in your browser. Approve it. Done.

That's the whole setup. No downloads, no project to clone. From here on, you're just chatting.

> **How to read this guide:** each step is **one thing to ask Claude Code**, shown in a code block, plus a quick note on *why it matters*. Copy the whole request, paste it in, watch it work, then go to the next step. They're written to be detailed on purpose — the more specific your ask, the better the result. Feel free to tweak them in your own words.

---

## Step 1 — Connect and read your inbox

```text
Connect to my Gmail account. To start, pull in my 10 most recent unread emails
so we can see them. For each one, show me the sender's name and email address,
the subject line, and a one-sentence summary of what they actually want. Lay it
out as a clean numbered list so I can scan my inbox at a glance and confirm
you're reading my real mail correctly.
```

**Why it matters:** This is your assistant taking its first look at your real inbox. Seeing it actually read your mail makes everything after this feel real.

---

## Step 2 — Gather your real writing

```text
Now I want to gather examples of how I actually write. Go through my Sent mail
and find emails I wrote as replies to other people. For each reply, also pull in
the original email I was responding to, so we keep them together as a pair: the
message that came in, and exactly how I answered it. Collect a few dozen of
these pairs across different kinds of conversations, and skip anything automated
or one-line. When you're done, show me five of the pairs side by side so I can
see the raw material we'll use to learn my voice.
```

**Why it matters:** Your voice isn't a vibe — it's learned from how you *actually* write. Pairing each reply with the email it answered teaches the assistant not just your words, but how you respond to different situations.

---

## Step 3 — Learn your voice

```text
Read carefully through all of those reply pairs and study how I write — not just
my words, but how my tone, length, and phrasing change depending on the
situation. Then write me a "voice profile": a short document with a separate
section for each kind of email I send (for example: sales, customer support,
mentoring, admin, partnerships). In each section, describe my tone, how long I
tend to write, my sentence rhythm, how I open and how I sign off, and include
one or two short phrases I use word-for-word. Use your most capable model for
this, since it's the heart of the whole thing, and save the profile so we can
reuse it later.
```

**Why it matters:** Read it aloud. It should sound like a friend describing how you email. This profile is what makes drafts sound like you and not a generic robot.

---

## Step 4 — Peek at how it finds the right reply

```text
Before we go further, I want to understand the technology underneath this. Pick
two of my past replies that are about similar topics, and two that are about
very different topics. Turn each reply into an "embedding" — a long list of
numbers that captures its meaning. Show me a short snippet of those numbers,
then measure how similar each pair is and show me the scores. Finally, explain
in plain English what just happened, and why two emails about similar things end
up with similar numbers.
```

**Why it matters:** An **embedding** is just turning text into numbers so that things that *mean* similar things sit close together. That's the trick your assistant uses to find your most relevant past reply and the right facts — no magic, just "close meanings sit close."

---

## Step 5 — Give it your facts

```text
My assistant should only ever state things that are actually true about me and
my work, so let's write those facts down. Help me create a few short notes: one
covering my main product or service and its real pricing, one covering any
upcoming event with its date and key details, and one covering my partnership or
sponsorship terms and rates. Ask me for the real numbers wherever you don't
already know them, keep each note short and factual, and treat these notes as my
single source of truth — the assistant must never state a price, date, or detail
that isn't written in them.
```

**Why it matters:** These notes are your assistant's source of truth. The golden rule: **no file, no fact.** If it isn't written here, the assistant isn't allowed to say it — that's what stops it from making things up.

---

## Step 6 — Make it searchable

```text
Now make everything we've created searchable. Build two separate searchable
libraries: one over my voice profile and example replies, so the assistant can
look up "how do I usually sound in a situation like this?", and a second one
over my fact notes, so it can look up "what's actually true about this?". Keep
the two completely separate so my writing style never gets mixed up with my
facts. Once they're built, test it: give it a sample incoming email and show me
the closest past reply and the relevant facts it pulls back.
```

**Why it matters:** Two libraries, two jobs. One answers "how would I say this?" and the other answers "what's actually true?" Keeping them apart keeps your *style* from getting tangled up with your *facts*.

---

## Step 7 — Write your rules

```text
Write me a "principles" document — the firm rules every single reply must
follow, no matter what. Include at least these: never state a fact that isn't in
my notes; never offer, hint at, or negotiate a discount; never make a
commitment, promise, or guarantee on my behalf; always sound like a real human,
never stiff or robotic; and never actually send anything — only ever save a
draft for me to review. Mark the most important ones as hard rules. And make it
explicit that these principles override my voice profile: if my natural style
ever conflicts with a rule — say my past emails were generous with discounts —
the rule wins, and the assistant holds back and leaves it to me.
```

**Why it matters:** Your voice profile is *style*; your principles are *policy*. **When they conflict, principles win.** Your past emails might offer a discount — but if a principle says never do that, the assistant holds back and leaves it to you.

---

## Step 8 — Discover your categories and build a classifier

```text
Look across my real emails and work out the categories I genuinely deal with —
my own buckets, like new leads, pricing questions, current students, or
partnerships — rather than generic labels. Once we've agreed on the categories,
build a classifier: something that reads any new incoming email and tags it with
which category it belongs to, how confident it is, what the sender actually
wants, how urgent it is, and whether it needs me personally. Set it so anything
sensitive — discount or refund requests, commitments, deals, or an upset sender
— gets flagged for me and is never answered automatically. Use a fast,
inexpensive model for this, since it runs on every email.
```

**Why it matters:** Your inbox is yours — your buckets should be too. Flagging the sensitive stuff for a human is how the assistant knows what *not* to touch on its own.

---

## Step 9 — Sort your inbox

```text
Now run that classifier across my unread emails and show me the results as a
triage view. For each email, show who it's from, the category you gave it, and
what should happen to it: should the assistant draft a reply, should it come
straight to me because it's sensitive, or should it be skipped because it's
automated or doesn't need a response? Give a one-line reason for each decision
so I can sanity-check how it's routing my inbox before we write a single reply.
```

**Why it matters:** This is triage. In one pass you see your whole inbox organized by what actually needs to happen, before a single reply is written.

---

## Step 10 — Write the replies (the writer)

```text
Now build the writer — the part that actually drafts replies. For each email
worth answering, have it write a response as me: in the voice from my profile,
using only the facts from my notes, and obeying every one of my principles.
Before it writes, it should pull in my closest past reply and the relevant facts
to ground itself. Have it stream the reply onto the screen as it's being written
so I can watch it come together, and use your most capable model since this is
the part people will judge. If it's ever missing a fact it needs, it should ask
for it rather than make something up.
```

**Why it matters:** This is the writer agent doing its main job. Notice it only uses facts from your notes and stays inside your rules. Drafts, never sends.

---

## Step 11 — Review the replies (the reviewer)

```text
Now add a second, independent agent — the reviewer — that checks every draft
before I ever see it. For each draft, have it answer three questions: is every
fact in it actually backed by my full set of notes, does it genuinely sound like
me, and does it break any of my principles? If a draft passes all three, approve
it. If it fails any of them, send it back to the writer with a note on what's
wrong and have it rewritten once. Use a fast model here. Then show me the verdict
for each draft — approved or sent back, and why — so I can watch the two agents
work together.
```

**Why it matters:** One agent writes, a different agent checks. That second pair of eyes — *grounded? sounds like you? breaks a rule?* — is the reason you can actually trust the drafts.

---

## Step 12 — Run the whole thing

```text
Now let's run the whole thing as one pipeline, start to finish: fetch my unread
inbox, sort every email into its category, draft replies for the ones that need
them, run each draft through the reviewer, and save all the results — the
original email, its category, the draft, and the review — so I can look back over
everything in one place. Walk through it on screen as it goes, so I can see each
email move through the stages.
```

**Why it matters:** Everything you built clicks together into one flow. Fetch → sort → write → review → save, all in a single go.

---

## Step 13 — Approve your drafts, one at a time

```text
Finally, let me approve the drafts one at a time. Show me my finished drafts as
a numbered list, then let me go through them individually — for each one I'll
either approve it, skip it, or tweak the wording first. When I approve a draft,
save it into my Gmail Drafts folder, ready for me to open and send myself. Never
send anything automatically — the final send is always my decision.
```

**Why it matters:** You're the human in the loop. You approve each draft individually, and approving simply parks it in Gmail Drafts. **You hit send yourself — always.**

---

## What you walk away with

A real email assistant that triages your inbox and writes like you — and that you can actually *trust*, because it only speaks from your facts, follows your rules, and never sends a thing without you. You didn't write a line of code. You built it by directing Claude Code in plain English, the same way you'd brief a sharp teammate. That's the whole point: you described what you wanted, and it got built. Now go make it yours. 🚀
