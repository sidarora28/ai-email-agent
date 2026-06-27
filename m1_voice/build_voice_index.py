"""build_voice_index.py — M1 Step 2 (R1.7): the reviewer's voice index.

Embeds each pair as [reply + the email it answered] into a local Chroma index.
At review time, the reviewer queries this with a draft to pull Sid's closest
real reply and check the draft is "close enough" to how he actually writes.

    python m1_voice/build_voice_index.py
"""

import json
import os
import time
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

PAIRS = Path(os.getenv("VOICE_PAIRS", "data/voice_pairs.jsonl"))
INDEX = os.getenv("VOICE_INDEX", "data/voice_index.db")
MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
COLLECTION = "voice"


def load_pairs():
    pairs = []
    with PAIRS.open() as f:
        for line in f:
            line = line.strip()
            if line:
                pairs.append(json.loads(line))
    return pairs


def embed_text(pair):
    """R1.7: index over reply + the email it answered."""
    inc = pair.get("incoming", {})
    rep = pair.get("reply", {})
    return f"INCOMING: {inc.get('body','')}\n\nREPLY: {rep.get('body','')}"


def main():
    pairs = load_pairs()
    print(f"Read {len(pairs)} pairs from {PAIRS}")

    print(f"Loading model {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=INDEX)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    col = client.create_collection(COLLECTION)

    print(f"Embedding {len(pairs)} pairs ...")
    start = time.time()
    texts = [embed_text(p) for p in pairs]
    vectors = model.encode(texts, batch_size=64, show_progress_bar=True)
    col.add(
        ids=[p["id"] for p in pairs],
        embeddings=[v.tolist() for v in vectors],
        documents=[p["reply"]["body"] for p in pairs],
        metadatas=[{
            "incoming_subject": p["incoming"].get("subject", ""),
            "incoming_body": p["incoming"].get("body", "")[:500],
        } for p in pairs],
    )
    print(f"Done. Voice index ({len(pairs)} pairs) in {time.time()-start:.1f}s -> {INDEX}")


if __name__ == "__main__":
    main()
