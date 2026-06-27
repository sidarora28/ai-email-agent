# Extension notes

This kit ships with magic numbers (one taxonomy, a 0.7 confidence threshold,
10 workers). That's deliberate — it runs in 5 minutes. Below is what you'd
build next, and what the cohort goes deep on.

## Eval methodology
- Hand-label a held-out set of ~50–100 emails — this is your ground truth.
- Score the classifier against it: per-category precision/recall, plus a
  confusion matrix to see *which* categories get mistaken for each other.
- Re-run evals on every prompt or taxonomy change. No eval set = flying blind.

## Threshold tuning
- The 0.7 in your routing logic is a placeholder, not a law of nature.
- Plot confidence vs. actual correctness and pick the threshold that hits your
  target precision. High-stakes auto-actions want a higher bar than triage.
- Different categories may deserve different thresholds.

## Multi-label
- Real emails are often two things at once (a billing question *and* a churn
  signal). Move from one category to a ranked list with per-label scores.
- Decide downstream behavior: act on the top label, or all above threshold?

## Active learning
- Don't label randomly. Surface the *low-confidence* and *disagreement* cases
  for human review — that's where each new label teaches the model the most.
- Feed corrected examples back into the prompt (few-shot) or your eval set, and
  watch the confusion matrix tighten over time.

The cohort's week 2 is exactly this loop: eval → measure → tune → relabel.
