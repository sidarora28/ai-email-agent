"""show_similar.py — DEMO the embeddings concept: semantic search over your voice.

Type any new email text; it embeds that text and returns your most similar past
replies from the voice index. This is the visible proof of "embeddings" —
matching by *meaning*, not keywords. (The classifier does NOT use this; embeddings
power voice retrieval + grounding.)

    python m1_voice/show_similar.py "can I get a discount on the course?"
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "m3_engine"))
from retrieve import retrieve_voice  # noqa: E402  (sets quiet env)

BOLD, DIM, GREEN, RESET = "\033[1m", "\033[2m", "\033[32m", "\033[0m"


def main():
    query = " ".join(sys.argv[1:]).strip() or sys.stdin.read().strip()
    if not query:
        print("Give me an email to match, e.g.:  python m1_voice/show_similar.py \"what's the price?\"")
        return
    print(f"\n🔎  {BOLD}Embeddings search{RESET} {DIM}— your closest past replies by meaning{RESET}")
    print(f"{DIM}    query: \"{query[:70]}\"{RESET}\n")
    for i, r in enumerate(retrieve_voice(query, 5), 1):
        print(f"  {GREEN}{i}.{RESET} {r['text'][:180].strip()}\n")


if __name__ == "__main__":
    main()
