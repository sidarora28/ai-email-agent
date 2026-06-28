You are analysing how I write emails, to build a reusable voice profile for an
assistant that will draft replies in my style.

You are given PAIRS of [incoming email] -> [my reply]. Study how my tone, length,
and phrasing change with the situation.

Do two things:

1. Discover the natural SITUATIONS I write in (e.g. sales/prospect, cohort
   support, mentorship, admin, partnership, personal). Use 4-7 categories that
   actually fit this corpus — don't force generic ones.

2. Write a human-readable VOICE PROFILE in Markdown, one `## ` section per
   situation. For each: tone, typical length, sentence rhythm, formatting, how
   I open and close, and 1-2 short verbatim phrases that are characteristic.

Then, at the very end, output the category list as a fenced yaml block EXACTLY
like this (machine-read):

```yaml
categories:
  - name: snake_case_name
    description: one line on what belongs here
```

Output only the Markdown profile followed by the single yaml block. No preamble.
