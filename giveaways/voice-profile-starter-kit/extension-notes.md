# Where the cohort takes this

This starter kit gets you a working voice profile: your sent emails, embedded
locally, searchable by similarity. That's the foundation. Here's what we build
on top of it in the cohort.

## 1. Corpus curation
Raw sent mail is noisy — auto-replies, one-liners, forwards, threads where you
quoted more than you wrote. We teach how to filter, dedupe, and weight your
corpus so the profile reflects your *real* voice, not your busiest day.

## 2. Re-ranking
Nearest-neighbor search is a first pass, not the final answer. We layer a
re-ranker on top of the embedding results to reorder candidates by true
relevance — so the reply you'd actually send floats to the top.

## 3. Voice evaluation
How do you *know* a generated reply sounds like you? We build a voice-eval
harness: held-out emails, similarity baselines, and rubric-based scoring so you
can measure drift and improvement instead of eyeballing it.

## 4. Multi-voice profiles
One person writes differently to a customer, a board member, and a teammate.
We extend the single profile into multiple personas (see `examples/`) and route
inbound mail to the right voice automatically.

From there: drafting, human-in-the-loop review, and wiring it into your inbox.
