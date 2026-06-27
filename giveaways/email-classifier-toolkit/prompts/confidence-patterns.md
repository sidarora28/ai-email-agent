# Confidence scoring patterns

How to think about the `confidence` field the agent returns (0.0–1.0).

- **Confidence is calibration, not vibes.** A 0.9 should be *right* ~9 times
  out of 10. If your 0.9s are wrong half the time, the score is decorative.
- **Anchor the extremes first.** 0.95+ = unambiguous, textbook example of the
  category. Below 0.5 = the model is essentially guessing — treat as "unsure".
- **The middle band is where the work is.** 0.6–0.8 means "probably right, but
  a human glance wouldn't hurt." This is the band your threshold lives in.
- **Penalize overlap.** When two categories both fit (a sales lead who is also
  an existing customer), confidence should drop — ambiguity is real signal.
- **Penalize thin input.** A one-line snippet with no body deserves lower
  confidence than a full message, even if the guess feels obvious.
- **Don't reward verbosity.** A long email isn't automatically a confident
  classification; length and certainty are unrelated.
- **Route by confidence, not just category.** Auto-act on high confidence,
  queue mid confidence for review, and flag low confidence for a human.
- **Confidence only matters if you measure it.** Log predicted confidence vs.
  actual correctness, then plot it — that's how you find your real threshold.
