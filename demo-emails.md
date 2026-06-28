# 📨 Demo emails — send to yourself before the show

Send these to **sid.arora.87@gmail.com** (ideally from another address so the sender
looks real). One per category. A few are deliberately **messy/multi-part** to stress
the classifier, the grounding, and the reviewer on stage. Each note says what it shows.

---

### 1. Lead nurture — *clean auto-draft, multi-question grounding*
Shows the drafter answering several real questions from `course.md` in your voice.

> **Subject:** A few questions before I commit to the July cohort
>
> Hi Sid, I've been lurking on your newsletter for a while and I'm seriously
> considering the cohort. Before I pull the trigger, a few things:
> 1. I'm a marketer with zero coding background — will I actually be able to keep up?
> 2. What are the three products we build, and do I get to keep them?
> 3. I work full-time — realistically how many hours a week is this?
> 4. If I can't make a live session, are the recordings enough to not fall behind?
>
> Trying to make sure this is the right fit before I pay. Thanks! — Priya

---

### 2. Price negotiation — *routes to YOU; emotional + layered*
Shows `needs_human` firing, and the reviewer killing any draft that offers a discount.

> **Subject:** Really want in but the price is rough
>
> Hey Sid, I'll be honest — I've wanted to do this since your last masterclass, but
> I just got laid off and $600 is genuinely out of reach right now. I saw the early
> bird is for the first 25 and I think I've missed it. Is there any kind of
> scholarship, a payment plan, or even a partial seat? I'm not trying to lowball you
> — I'd happily write a testimonial or help out however I can. I really believe this
> could change my trajectory. Anything you can do? — Daniel

---

### 3. Sales / persuasion — *high-conviction pitch, named competitor, objection stack*
Shows the drafter persuading without discounting, grounded in real differentiators.

> **Subject:** Why this over [competitor] or just the recordings?
>
> Sid, straight up — I'm comparing your cohort to a $200 self-paced Udemy course and
> honestly just watching free YouTube builds. Three objections I can't get past:
> (a) why is yours 3x the price, (b) what do I actually get that a recording can't
> give me, and (c) I've started cohorts before and ghosted by week 2 — what makes
> this different? Convince me or I'll save the money. — Marcus

---

### 4. Student admin — *mixes auto-handle + escalate; missing info*
Shows a live payment/registration check, an ask-for-email when it can't find them,
AND `needs_human` on the unrecognized-charge part (refund-adjacent).

> **Subject:** Paid but no Slack invite + a charge I don't recognize
>
> Hi Sid, two things. First, I paid for the July cohort two days ago but never got
> the Slack invite — can you check my registration went through? I might have used
> my work email (a.okafor@acme.co) rather than this one. Second, and this is
> stressing me out, I see a second $600 charge on my card from what looks like the
> same checkout. Did I get billed twice? If so I need that refunded. Can you sort
> both out? Thanks, Aisha

---

### 5. Cohort mentorship — *candid advice, grounded in the stack*
Shows the drafter giving real, specific guidance (and offering to continue on Slack).

> **Subject:** Is my Week 3 idea too big — and what do I build it on?
>
> Sid, for my own-idea build I want to make a two-sided marketplace where freelancers
> list services and clients book + pay them. I know you said scope to a 7-day v1 but
> I'm worried payments + two user types is too much. Should I cut it down, and if so
> to what? Also — would you use Supabase RLS for keeping each user's data separate,
> or is that overkill for a v1? Don't want to over-engineer it. Bit anxious I'm
> behind. Honest take appreciated. — Tom

---

### 6. Brand partnership — *routes to YOU; custom bundle, discount, guarantees, deadline*
Shows the rate card being shared but every custom term / guarantee / discount deferred.

> **Subject:** Sponsorship — custom bundle + a few asks
>
> Hi Sid, I run partnerships at an AI dev-tools startup and we'd love to work with
> JustAnotherPM. We're thinking a 6-month deal across the newsletter, LinkedIn, and
> a couple of Twitter threads. A few things:
> - Can you put together a custom bundle price for that mix? Our budget is ~$15k.
> - Given the volume + length of commitment, what kind of discount can you do?
> - We'd need a guaranteed minimum of clicks/leads per post to get sign-off internally.
> - We'd want to approve copy, and we're trying to lock this before our quarter ends
>   Friday.
>
> Can you confirm the bundle, the discount, and the performance guarantee so I can
> take it to my VP? — Rebecca, Head of Partnerships

---

### 7. Admin / vendor — *threaded, scheduling + grounded correction*
Shows a calendar check, plus the assistant correctly declining to promise a recording
(event is live-only) rather than inventing an answer.

> **Subject:** Re: tech run-through for your masterclass
>
> Hey Sid, following up on my last note. Can we lock 30 minutes Tuesday or Wednesday
> morning next week for the tech run-through? I'll send a calendar invite once you
> confirm a slot. Two quick things to confirm on your side: what attendee cap should
> we set the room to, and will you want us to record the session so you can share the
> replay afterwards? Want to get the room configured correctly. — Jordan, Events Platform

---

## How to use these on stage
- Send all 7 a few minutes before you go on, so `fetch-emails.sh` pulls a full, varied inbox.
- The clean ones (**1, 5**) show smooth auto-drafts in your voice.
- The escalations (**2, 6**, and part of **4**) show `needs_human` and the reviewer guarding your principles.
- **4** and **7** show grounding/connectors — verifying a payment, checking the calendar, and *not* inventing a fact (no replay).
