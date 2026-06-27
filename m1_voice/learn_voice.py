"""learn_voice.py — M1 Step 2: turn the pairs into a written voice profile.

Claude Opus 4.8 reads the [incoming → reply] pairs, discovers the natural
situations Sid writes in, groups the pairs, and writes a human-readable style
profile per situation (tone, length, rhythm, formatting, openings/closings).

Outputs:
  - data/voice_profile.md   the style guide (per situation)
  - data/categories.yaml    the discovered categories (name + description) for M2

    python m1_voice/learn_voice.py

Requirements: R1.5 (group by situation), R1.6 (Opus 4.8 writes the profile).
"""

import json
import os
import re
import subprocess
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PAIRS = Path(os.getenv("VOICE_PAIRS", "data/voice_pairs.jsonl"))
PROFILE = Path(os.getenv("VOICE_PROFILE", "data/voice_profile.md"))
CATEGORIES = Path("data/categories.yaml")
MODEL = os.getenv("VOICE_PROFILE_MODEL", "claude-opus-4-8")

INSTRUCTION = """You are analysing how Sid writes emails, to build a reusable
voice profile for an assistant that will draft replies in his style.

You are given PAIRS of [incoming email] -> [Sid's reply]. Study how his tone,
length, and phrasing change with the situation.

Do two things:

1. Discover the natural SITUATIONS he writes in (e.g. sales/prospect, cohort
   support, mentorship, admin, partnership, personal). Use 4-7 categories that
   actually fit this corpus — don't force generic ones.

2. Write a human-readable VOICE PROFILE in Markdown, one `## ` section per
   situation. For each: tone, typical length, sentence rhythm, formatting, how
   he opens and closes, and 1-2 short verbatim phrases that are characteristic.

Then, at the very end, output the category list as a fenced yaml block EXACTLY
like this (machine-read):

```yaml
categories:
  - name: snake_case_name
    description: one line on what belongs here
```

Output only the Markdown profile followed by the single yaml block. No preamble.
"""


def load_pairs():
    pairs = []
    with PAIRS.open() as f:
        for line in f:
            line = line.strip()
            if line:
                pairs.append(json.loads(line))
    return pairs


def render_pairs(pairs):
    out = []
    for i, p in enumerate(pairs, 1):
        inc = p.get("incoming", {})
        rep = p.get("reply", {})
        out.append(
            f"--- PAIR {i} ---\n"
            f"INCOMING (subject: {inc.get('subject','')}):\n{inc.get('body','')}\n\n"
            f"SID'S REPLY:\n{rep.get('body','')}\n"
        )
    return "\n".join(out)


def call_opus(prompt: str) -> str:
    result = subprocess.run(
        ["claude", "-p", prompt, "--model", MODEL],
        capture_output=True, text=True, timeout=600,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr[:300]}")
    return result.stdout.strip()


def split_output(text: str):
    """Separate the markdown profile from the trailing ```yaml categories block."""
    m = re.search(r"```yaml\s*(.*?)```", text, re.DOTALL)
    yaml_block = m.group(1).strip() if m else "categories: []"
    profile = text[: m.start()].strip() if m else text.strip()
    return profile, yaml_block


def main():
    pairs = load_pairs()
    print(f"Read {len(pairs)} voice pairs from {PAIRS}")
    print(f"Asking {MODEL} to discover situations and write the voice profile ...")

    prompt = f"{INSTRUCTION}\n\nPAIRS:\n{render_pairs(pairs)}"
    out = call_opus(prompt)
    profile, categories_yaml = split_output(out)

    PROFILE.parent.mkdir(parents=True, exist_ok=True)
    PROFILE.write_text(profile + "\n")
    CATEGORIES.write_text(categories_yaml + "\n")

    n_cats = categories_yaml.count("- name:")
    print(f"Wrote voice profile -> {PROFILE}")
    print(f"Wrote {n_cats} discovered categories -> {CATEGORIES}")


if __name__ == "__main__":
    main()
