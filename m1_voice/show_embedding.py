"""show_embedding.py — make an embedding VISIBLE.

Takes a real chunk of your knowledge (course.md by default), shows the text, then
shows the actual numbers it becomes, then shows that a RELATED question scores
high and an UNRELATED one scores low. That's the whole idea of embeddings:
meaning turned into numbers you can compare.

    python m1_voice/show_embedding.py
"""

import os
import sys
import warnings
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
warnings.filterwarnings("ignore")

import numpy as np  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BOLD, DIM, GREEN, YELLOW, RESET = "\033[1m", "\033[2m", "\033[32m", "\033[33m", "\033[0m"


def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # a real piece of your knowledge base
    arg = " ".join(sys.argv[1:]).strip()
    if arg:
        text = arg
    else:
        course = (ROOT / "knowledge/course.md").read_text()
        # grab the pricing-ish paragraph for a relatable example
        text = next((p.strip() for p in course.split("\n\n")
                     if "$" in p or "price" in p.lower()), course[:300]).strip()

    vec = model.encode([text])[0]

    print(f"\n{BOLD}1) The text (a real chunk of your knowledge):{RESET}")
    print(f"{DIM}{text[:300]}{RESET}\n")

    print(f"{BOLD}2) The same text as an EMBEDDING — {len(vec)} numbers (first 12 shown):{RESET}")
    print(f"{DIM}{np.round(vec[:12], 3).tolist()} …{RESET}\n")

    print(f"{BOLD}3) Why that's useful — compare by MEANING, not words:{RESET}")
    related = "How much does the course cost?"
    unrelated = "What time is the football match tonight?"
    rs = cosine(vec, model.encode([related])[0])
    us = cosine(vec, model.encode([unrelated])[0])
    print(f"   {GREEN}{rs:.2f}{RESET}  \"{related}\"   {DIM}(related → high){RESET}")
    print(f"   {YELLOW}{us:.2f}{RESET}  \"{unrelated}\"   {DIM}(unrelated → low){RESET}\n")
    print(f"{DIM}That score is how the assistant finds the right facts and your "
          f"closest past replies.{RESET}\n")


if __name__ == "__main__":
    main()
